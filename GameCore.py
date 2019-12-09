from GameClasses import *
import Global
from queue import Queue
import random


circle = Circle(1, 2, 3 , 4, 5, 6, 7, 8)


def game_init():
    pass

def input_data(data):
    Global.operate_queue.put(data)


def output_data():
    return Global.output_dict

def item_refresh():
    if Global.time%60 ==0:
        for i in range(len(Global.tank_list)):
            x = random.randint(circle.current_x1, circle.current_x2)
            y = random.randint(circle.current_y1, circle.current_y2)
            type_id = random.randint(0, 1)
            Global.item_changed.append(Item(x, y, type_id))
            x = random.randint(circle.current_x1, circle.current_x2)
            y = random.randint(circle.current_y1, circle.current_y2)
            type_id = random.randint(0, 1)
            Global.item_changed.append(Item(x, y, type_id))

def is_over():
    if len(Global.tank_list) == 1:
        return True
    else:
        return False


def gaming():
    #operation_num = operate_queue.qsize()

    while not Global.operate_queue.empty():
        operate = Global.operate_queue.get()

        tank_id = operate[0]
        up = operate[1]
        down = operate[2]
        left = operate[3]
        right = operate[4]
        fire = operate[5]
        tank = Global.tank_list[tank_id]
        tank.shoot(fire)
        tank.drive(up, down, left, right)

        for ammo in Global.ammo_list:
            ammo.move()
            ammo.refresh()

        circle.refresh()
        item_refresh()

        Global.output_dict['tank'] = Global.tank_list
        Global.output_dict['ammo'] = Global.ammo_list
        Global.output_dict['brick'] = Global.brick_changed
        Global.output_dict['item'] = Global.item_changed

        


