import math
import Global
import random

class Tank:

    def __init__(self, tank_id, hp, ammo, kill, x, y, direction):
        self.tank_id = tank_id
        self.hp = hp
        self.ammo = ammo
        self.kill = kill
        self.x = x
        self.y = y
        self.direction = direction 

    def shoot(self, fire):
        if fire==1:
            self.ammo = self.ammo - 1
            Global.ammo_num = Global.ammo_num + 1
            Global.ammo_list.append(Ammo(self.tank_id, Global.ammo_num, self.x, self.y, self.direction))


    def drive(self, up, down, left, right):
        if not self.is_in_circle():
            self.hp = self.hp - Global.poison

        self.direction = self.direction + (right - left)
        temp_x = self.x + math.sin(self.direction) * Global.tank_v*(up-down)
        temp_y = self.y - math.cos(self.direction) * Global.tank_v*(up-down)
        for tank in Global.tank_list:
            if 0.1<(temp_x - tank.x) * (temp_x - tank.x) + (temp_y - tank.y) * (temp_y - tank.y) <= 1.0:
                return
        for brick in Global.brick_list:
            if (-0.5 <= temp_x-brick.x <=1.5 )&(-0.5 <= temp_y-brick.y <=1.5):
                return

        self.x = temp_x
        self.y = temp_y
        for item in Global.item_list:
            if (-0.5 <= self.x - item.x <= 1.5) & (-0.5 <= self.y - item.y <= 1.5):
                item.disappear()
                Global.item_changed.append(item)
                if item.type_id ==0:
                    tank.hp = tank.hp + Global.item_hp
                elif  item.type_id ==1:
                    tank.ammo = tank.ammo+Global.item_ammo


    def is_in_circle(self):
        if (Global.current_x1<self.x<Global.current_x2)and(Global.current_y1<self.y<Global.current_y2):
            return True
        else:
            return False


class Ammo:

    def __init__(self, tank_id, ammo_id, x, y, direction):
        self.tank_id = tank_id
        self.ammo_id = ammo_id
        self.x = x
        self.y = y
        self.direction = direction
        self.exist = 1

    def move(self):
        self.x = self.x + math.sin(self.direction) * Global.ammo_v
        self.y = self.y - math.cos(self.direction) * Global.ammo_v

    def refresh(self):
        for tank in Global.tank_list:
            if (self.x-tank.x)*(self.x-tank.x)+(self.y-tank.y)*(self.y-tank.y) <= 0.25:
                tank.hp = tank.hp - Global.ammo_attack
                self.exist = 0

        for brick in Global.brick_list:
            if (0 < self.x-brick.x <=1 )&(0 < self.y-brick.y <=1):
                self.exist = 0
                brick.disappear()
                Global.brick_changed.append(brick)



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
                 target_x1, target_y1, target_x2, target_y2):
        self.current_x1 = current_x1
        self.current_y1 = current_y1
        self.current_x2 = current_x2
        self.current_y2 = current_y2
        Global.current_x1 = current_x1
        Global.current_y1 = current_y1
        Global.current_x2 = current_x2
        Global.current_y2 = current_y2
        self.target_x1 = target_x1
        self.target_y1 = target_y1
        self.target_x2 = target_x2
        self.target_y2 = target_y2

    def refresh(self):
        if Global.time%10==0:
            self.current_x1 = self.current_x1 + int(self.current_x1 < self.target_x1)
            self.current_y1 = self.current_y1 + int(self.current_y1 < self.target_y1)
            self.current_x2 = self.current_x2 + int(self.current_x2 < self.target_x2)
            self.current_y2 = self.current_y2 + int(self.current_y2 < self.target_y2)
            Global.current_x1 =  self.current_x1
            Global.current_y1 = self.current_y1
            Global.current_x2 = self.current_x2
            Global.current_y2 = self.current_y2

        if (self.current_x1 == self.target_x1)and(self.current_y1 == self.target_y1)and(self.current_x2 == self.target_x2)and(self.current_y2 ==self.target_y2):
            self.target_x1= self.target_x1 + random.randint(0, self.target_x2-self.target_x1)
            self.target_y1 = self.target_y1 + random.randint(0, self.target_y2-self.target_y1)
            self.target_x2 = self.target_x2 - random.randint(0, self.target_x2-self.target_x1)
            self.target_y2 = self.target_y2 - random.randint(0, self.target_x2-self.target_x1)
