from GameClasses import *
import random


class GameCore:
    def __init__(self, num):
        self.num = num
        self.info = GlobalInfo()
        self.circle = Circle(1,1,99,99,1,1,99,99, self.info)

    def game_init(self, server_dict):
        for tank in server_dict['tanks']:
            self.info.tank_list.append(Tank(tank[0],tank[1],tank[2],tank[3],tank[4],tank[5], tank[6],self.info))
        for brick in server_dict['obs']:
            self.info.brick_list.append(Brick(brick[0], brick[1]))


    def input_data(self,data):
        self.info.operate_queue.put(data)

    def output_data(self):
        return self.info.output_dict

    def item_refresh(self):
        if self.info.time % 60*30 == 0:
            for i in range(len(self.info.tank_list)):
                x = random.randint(self.circle.current_x1, self.circle.current_x2)
                y = random.randint(self.circle.current_y1, self.circle.current_y2)
                type_id = random.randint(0, 1)
                self.info.item_changed.append(Item(x, y, type_id))
                x = random.randint(self.circle.current_x1, self.circle.current_x2)
                y = random.randint(self.circle.current_y1, self.circle.current_y2)
                type_id = random.randint(0, 1)
                self.info.item_changed.append(Item(x, y, type_id))

    def check_winner(self):
        alive_count = 0
        alive_id = -1
        for t in self.info.tank_list:
            if t.hp > 0:
                alive_count = alive_count + 1
                alive_id = t.tank_id
        if alive_count == 1:
            self.info.winner = alive_id

    def refresh_output(self):

        self.info.information.clear()
        self.info.information.append(
            [0, self.info.winner, len(self.info.tank_list), len(self.info.ammo_list), len(self.info.brick_changed),
             len(self.info.item_changed)])
        self.info.tanks.clear()
        for tank in self.info.tank_list:
            self.info.tanks.append([tank.tank_id, tank.hp, tank.ammo, tank.kill, tank.direction, tank.x, tank.y])
        self.info.bulls.clear()
        for ammo in self.info.ammo_list:
            self.info.bulls.append([ammo.tank_id, ammo.ammo_id, ammo.exist, ammo.x, ammo.y])
        self.info.obs.clear()
        for brick in self.info.brick_changed:
            self.info.obs.append([brick.x, brick.y])
        self.info.props.clear()
        for item in self.info.item_changed:
            self.info.props.append([1, item.type_id, item.exist, item.x, item.y])
        self.info.safe.clear()
        self.info.safe.append([self.circle.current_x1, self.circle.current_y1,self.circle.current_x2,self.circle.current_y2,
             self.circle.target_x1, self.circle.target_y1,self.circle.target_x2,self.circle.target_y2])

    def list_refresh(self):
        for tank in self.info.tank_list:
            if tank.hp <= 0:
                self.info.tank_list.remove(tank)

        for ammo in self.info.ammo_list:
            if ammo.exist == 0:
                self.info.ammo_list.remove(ammo)

        for brick in self.info.brick_list:
            if brick.exist == 0:
                self.info.brick_list.remove(brick)

        self.info.brick_changed.clear()

        for item in self.info.item_list:
            if item.exist == 0:
                self.info.item_list.remove(item)

        self.info.item_changed.clear()

    def gaming(self):
        # operation_num = operate_queue.qsize()
        '''
        try:
            self.list_refresh()
            while not self.info.operate_queue.empty():
                operate = self.info.operate_queue.get()

                tank_id = operate[0]
                up = operate[1]
                down = operate[2]
                left = operate[3]
                right = operate[4]
                fire = operate[5]
                for t in self.info.tank_list:
                    if t.tank_id == tank_id:
                        tank = t
                        break
                tank.shoot(fire)
                tank.drive(up, down, left, right)

                for ammo in self.info.ammo_list:
                    ammo.move()
                    ammo.refresh()

                self.circle.refresh()
                self.item_refresh()
                self.check_winner()
                self.refresh_output()
                self.info.time = self.info.time + 1
        except Exception as e:
            print('GameCore Error', e)
        '''
        self.list_refresh()


        while not self.info.operate_queue.empty():

            operate = self.info.operate_queue.get()

            tank_id = operate[0]
            up = operate[1]
            down = operate[2]
            left = operate[3]
            right = operate[4]
            fire = operate[5]
            for t in self.info.tank_list:
                if t.tank_id == tank_id:
                    tank = t
                    tank.shoot(fire)
                    tank.drive(up, down, left, right)
                    break

            for ammo in self.info.ammo_list:
                ammo.move()
                ammo.refresh()

            self.circle.refresh()
            self.item_refresh()
            self.check_winner()
            self.refresh_output()
            self.info.time = self.info.time + 1
            if len(self.info.tank_list) == 1:
                return self.info.tank_list[0].tank_id
            else:
                return -1






