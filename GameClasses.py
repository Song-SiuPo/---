import math
from queue import Queue

import random

class GlobalInfo:
    time = 0
    length = 1
    poison = 0.1
    tank_v = 0.1
    # tank_size = 1
    ammo_v = 10
    ammo_attack = 10
    # circle_v = 1
    ammo_num = 0

    item_hp = 10
    item_ammo = 10

    current_x1 = 1
    current_y1 = 2
    current_x2 = 3
    current_y2 = 4

    brick_list = []
    item_list = []

    operate_queue = Queue()
    operate_dict = {}

    ammo_list = []
    tank_list = []
    brick_changed = []
    item_changed = []
    winner = -1


    information = []
    tanks = []
    bulls = []
    obs = []
    glass = []
    props = []
    safe = []


    output_dict = {'information':information,'tanks': tanks, 'bulls':bulls, 'obs': obs, 'props': props , 'safe': safe}


class Tank:

    def __init__(self, tank_id, hp, ammo, kill,  direction, x, y,info):
        self.tank_id = tank_id
        self.hp = hp
        self.ammo = ammo
        self.kill = kill
        self.x = x
        self.y = y
        self.direction = direction 
        self.info = info

    def shoot(self, fire):
        if fire==1:
            self.ammo = self.ammo - 1
            self.info.ammo_num = self.info.ammo_num + 1
            self.info.ammo_list.append(Ammo(self.tank_id, self.info.ammo_num, self.x, self.y, self.direction, self.info))


    def drive(self, up, down, left, right):
        if not self.is_in_circle():
            self.hp = self.hp - self.info.poison

        self.direction = self.direction + (right - left)
        temp_x = self.x + math.sin(self.direction) * self.info.tank_v*(up-down)
        temp_y = self.y - math.cos(self.direction) * self.info.tank_v*(up-down)
        for tank in self.info.tank_list:
            if 0.1<(temp_x - tank.x) * (temp_x - tank.x) + (temp_y - tank.y) * (temp_y - tank.y) <= 1.0:
                return
        for brick in self.info.brick_list:
            if (-0.5 <= temp_x-brick.x <=1.5 )&(-0.5 <= temp_y-brick.y <=1.5):
                return
        if temp_x >= 100 or temp_x <= 0 or temp_y >= 100 or temp_x <= 0:
            return
        self.x = temp_x
        self.y = temp_y
        for item in self.info.item_list:
            if (-0.5 <= self.x - item.x <= 1.5) & (-0.5 <= self.y - item.y <= 1.5):
                item.disappear()
                self.info.item_changed.append(item)
                if item.type_id ==0:
                    tank.hp = tank.hp + self.info.item_hp
                elif  item.type_id ==1:
                    tank.ammo = tank.ammo+self.info.item_ammo


    def is_in_circle(self):
        if (self.info.current_x1<self.x<self.info.current_x2)and(self.info.current_y1<self.y<self.info.current_y2):
            return True
        else:
            return False


class Ammo:

    def __init__(self, tank_id, ammo_id, x, y, direction, info):
        self.tank_id = tank_id
        self.ammo_id = ammo_id
        self.x = x
        self.y = y
        self.direction = direction
        self.exist = 1
        self.info = info
    def move(self):
        self.x = self.x + math.sin(self.direction) * self.info.ammo_v
        self.y = self.y - math.cos(self.direction) * self.info.ammo_v

    def refresh(self):
        if self.x >= 100 or self.x <= 0 or self.y >= 100 or self.x <= 0:
            self.exist = 0
            return
        for tank in self.info.tank_list:
            if (self.x-tank.x)*(self.x-tank.x)+(self.y-tank.y)*(self.y-tank.y) <= 0.25 and self.tank_id != tank.tank_id:
                tank.hp = tank.hp - self.info.ammo_attack
                self.exist = 0
                if tank.hp <= 0:
                    for t in self.info.tank_list:
                        if t.tank_id == self.tank_id:
                            t.kill = t.kill + 1   #这里可以加上杀人信息

        for brick in self.info.brick_list:
            if (0 < self.x-brick.x <=1 )&(0 < self.y-brick.y <=1):
                self.exist = 0
                brick.disappear()
                self.info.brick_changed.append(brick)
                self.info.brick_list.remove(brick)
                break





class Brick:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.exist = 1

    def disappear(self):
        self.exist = 0


class Grass:

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Item:

    def __init__(self, x, y, type_id):
        self.x = x
        self.y = y
        self.type_id = type_id
        self.exist = 1

    def disappear(self):
        self.exist = 0


class Circle:

    def __init__(self,
                 current_x1, current_y1, current_x2, current_y2,
                 target_x1, target_y1, target_x2, target_y2,  info):
        self.info = info
        self.current_x1 = current_x1
        self.current_y1 = current_y1
        self.current_x2 = current_x2
        self.current_y2 = current_y2
        self.info.current_x1 = current_x1
        self.info.current_y1 = current_y1
        self.info.current_x2 = current_x2
        self.info.current_y2 = current_y2
        self.target_x1 = target_x1
        self.target_y1 = target_y1
        self.target_x2 = target_x2
        self.target_y2 = target_y2

    def refresh(self):
        if self.info.time%10*30==0:
            self.current_x1 = self.current_x1 + int(self.current_x1 < self.target_x1)
            self.current_y1 = self.current_y1 + int(self.current_y1 < self.target_y1)
            self.current_x2 = self.current_x2 - int(self.current_x2 > self.target_x2)
            self.current_y2 = self.current_y2 - int(self.current_y2 > self.target_y2)
            self.info.current_x1 =  self.current_x1
            self.info.current_y1 = self.current_y1
            self.info.current_x2 = self.current_x2
            self.info.current_y2 = self.current_y2

        if (self.current_x1 == self.target_x1)and(self.current_y1 == self.target_y1)and(self.current_x2 == self.target_x2)and(self.current_y2 ==self.target_y2):
            self.target_x1= self.target_x1 + random.randint(0, self.target_x2-self.target_x1)
            self.target_y1 = self.target_y1 + random.randint(0, self.target_y2-self.target_y1)
            self.target_x2 = self.target_x2 - random.randint(0, self.target_x2-self.target_x1)
            self.target_y2 = self.target_y2 - random.randint(0, self.target_y2-self.target_y1)
