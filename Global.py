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


brick_list=[]
item_list=[]

operate_queue = Queue()
operate_dict = {}


ammo_list=[]
tank_list=[]
brick_changed = []
item_changed = []

output_dict={'tank':tank_list, 'ammo':ammo_list, 'brick':brick_changed, 'item':item_changed}