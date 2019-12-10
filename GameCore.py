from GameClasses import *
import random


class GameCore:
    def __init__(self, num):
        self.num = num
        self.info = GlobalInfo()
        self.circle = Circle(8, 7, 6, 5, 4, 3, 2, 1, self.info)

    def game_init(self):
        pass

    def input_data(self,data):
        self.info.operate_queue.put(data)

    def output_data(self):
        return self.info.output_dict

    def item_refresh(self):
        if self.info.time % 60 == 0:
            for i in range(len(self.info.tank_list)):
                x = random.randint(self.circle.current_x1, self.circle.current_x2)
                y = random.randint(self.circle.current_y1, self.circle.current_y2)
                type_id = random.randint(0, 1)
                self.info.item_changed.append(Item(x, y, type_id))
                x = random.randint(self.circle.current_x1, self.circle.current_x2)
                y = random.randint(self.circle.current_y1, self.circle.current_y2)
                type_id = random.randint(0, 1)
                self.info.item_changed.append(Item(x, y, type_id))

    def is_over(self):
        if len(self.info.tank_list) == 1:
            return True
        else:
            return False

    def gaming(self):
        # operation_num = operate_queue.qsize()

        while not self.info.operate_queue.empty():
            operate = self.info.operate_queue.get()

            tank_id = operate[0]
            up = operate[1]
            down = operate[2]
            left = operate[3]
            right = operate[4]
            fire = operate[5]
            tank = self.info.tank_list[tank_id]
            tank.shoot(fire)
            tank.drive(up, down, left, right)

            for ammo in self.info.ammo_list:
                ammo.move()
                ammo.refresh()

            self.circle.refresh()
            self.item_refresh()

            self.info.output_dict['tank'] = self.info.tank_list
            self.info.output_dict['ammo'] = self.info.ammo_list
            self.info.output_dict['brick'] = self.info.brick_changed
            self.info.output_dict['item'] = self.info.item_changed




