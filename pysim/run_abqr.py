import torch
import arcsim
import json
import sys
import gc
import os
import copy
import numpy as np
import time



sim = arcsim.get_sim()

def reset_sim(sim):
	arcsim.init_physics('conf/rigidcloth/absparse/abqr_make.json','200204_qr/out',False)



def get_loss(sim):
	diffs = []
	for o in sim.obstacles:
		diffs.append(o.curr_state_mesh.dummy_node.x.norm())
	return torch.stack(diffs).mean()

def run_sim(sim):
	for step in range(1):
		arcsim.sim_step()
		print(step)



perline = 50

def make_json (max_block = 1):
	with open('conf/rigidcloth/absparse/multi.json','r') as f:
		config = json.load(f)

	cube   = config['obstacles'][0]
	ground = config['obstacles'][1]


	single_length = 0.1

	one_dif       = single_length + 0.001

	ini_size      = single_length
	ini_x         = -4
	ini_y         = -4

	def save_config(config, file):
		with open(file,'w') as f:
			json.dump(config, f)
	
	ground['transform']['scale'] = max_block


	cube['transform']['translate'][0] = ini_x
	cube['transform']['translate'][2] = 0.01

	for i in range(1, max_block):
		
		new_prim = copy.deepcopy(cube)
		new_prim['transform']['translate'][2] = 0.001 + single_length + 0.001
		new_prim['transform']['translate'][0] = ini_x + one_dif * (i-0.5)
		new_prim['transform']['translate'][1] = new_prim['transform']['translate'][1] + 0.01
		config['obstacles'].append(new_prim)

		new_prim = copy.deepcopy(cube)
		new_prim['transform']['translate'][0] = ini_x + one_dif * i
		new_prim['transform']['translate'][2] = 0.001
		config['obstacles'].append(new_prim)


	# cube['transform']['translate'][0] = ini_x
	# cube['transform']['translate'][2] = 0.0001

	# for i in range(1, max_block):
		
	# 	new_prim = copy.deepcopy(cube)
	# 	new_prim['transform']['translate'][2] = i * single_length 
	# 	new_prim['transform']['translate'][0] = ini_x 
	# 	new_prim['transform']['translate'][1] = new_prim['transform']['translate'][1] + 0.0001
	# 	config['obstacles'].append(new_prim)



	save_config(config, "conf/rigidcloth/absparse/abqr_make.json")

print(sys.argv)

max_line = int(sys.argv[1])

print("max_line")
print(max_line)
make_json(max_line)


#arcsim.msim(4,['arcsim','simulateoffline','conf/rigidcloth/multibody/multibody_make.json','out'])
#arcsim.msim(4,['arcsim','simulate','conf/rigidcloth/multibody/multibody_make.json','out'])
# sim = arcsim.get_sim()
reset_sim(sim)
g = sim.gravity
g.requires_grad = True

run_sim(sim)

optimizer = torch.optim.SGD([{'params':g,'lr':0.1}],momentum=0.9)
optimizer.zero_grad()

loss = get_loss(sim)
t = time.time()
loss.backward()

time_record = time.time() - t
time_per    = time_record / (max_line*perline)
print("total backward:---- %f" % time_record)

