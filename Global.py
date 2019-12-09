from queue import Queue

time = 0
length = 1
poison = 0.1
tank_v = 0.1
#tank_size = 1
ammo_v = 0.1
ammo_attack = 10
#circle_v = 1
ammo_num =0

item_hp = 10
item_ammo = 10

ammo_list=[]
tank_list=[]
brick_list=[]
item_list=[]

operate_queue = Queue()
operate_dict = {}

output_dict={}



brick_changed = []
item_changed = []