from GameClasses import *
import Global

def game_init():
    Global.time = 0
    Global.tank_v = 0.1
    # tank_size = 2
    Global.ammo_v = 0.1
    Global.ammo_attack = 10
    # circle_v = 1
    Global.ammo_num = 0

    Global.ammo_list = []
    Global.tank_list=[]
    Global.brick_list=[]
    Global.item_list=[]

    Global.operate_queue = Global.Queue()
    Global.operate_dict = {}
    Global.output_dict = {}


def input_data(data):
    Global.operate_queue.put(data)


def output_data():
    return Global.output_dict