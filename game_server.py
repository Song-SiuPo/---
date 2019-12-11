"""
作者： mieyangyanga
文件描述：游戏服务器类
"""

import socket
import threading
import time
from queue import Queue
import GameCore
from pack_data import *
from stop_thread import stop_thread

class Game_server():
    def __init__(self):
        # 服务器是否运行
        self.stop_send = False
        self.stop_receive = False
        self.stop_handle = False
        # 服务器socket
        self.server_socket = None


        # 接受到的客户端的消息队列
        self.message_queue = Queue()
        # 要发送给客户端的消息队列，格式：(data, addr)
        self.message_to_send = Queue()
        # 等待中的玩家队列
        self.player_queue = Queue()

        # 单局最大玩家数量
        self.max_num = 10

        # 玩家的id与ip的字典,接收请求开始游戏的消息时处理
        self.players_ip = {}
        # 玩家id与所在的游戏的id，开始游戏初始化时处理
        self.players_game = {}

        # 当前的游戏id
        self.cur_game_id = 10000
        # 游戏的id与要发给对应游戏的消息队列
        self.game_message = {}

        # 接收消息的线程
        self.receive_thread = threading.Thread(target=self.receive_data,args=())
        # 发送数据的线程
        self.send_thread = threading.Thread(target=self.send_data,args=())
        # 处理消息的线程
        self.handle_thread = threading.Thread(target=self.handle_message,args=())
        # 处理每局游戏的线程,格式：{id:Thread}
        self.games_threads = {}

    def get_message_send_len(self):
        return self.message_to_send.qsize()

    # 获取当前所有的游戏线程
    def get_games_thread(self):
        return self.games_threads

    # 获取玩家信息
    def get_players(self):
        return self.players_ip

    # 获取玩家所在的对局
    def get_players_in_game(self):
        return self.players_game

    # 获取等待进入游戏的玩家
    def get_players_in_queue(self):
        return self.player_queue

    # 开始游戏服务器
    def run(self, host, port):
        """
        调用以开始游戏服务器
        :param host: 服务器绑定的主机地址 "10.128.181.188"
        :param port: 端口号 23456
        绑定主机并开始服务器的其他线程
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.server_socket.bind((host, port))
        except Exception as e:
            raise e

        self.begin_receive()
        self.begin_send()
        self.begin_handle()
        # 服务器功能扩展
        print("服务器已启动")

    # 派生线程接收数据
    def begin_receive(self):
        self.receive_thread.start()

    def get_receive_thread(self):
        return self.receive_thread.getName()

    # 派生线程发送数据
    def begin_send(self):
        self.send_thread.start()

    def get_send_thread(self):
        return self.send_thread.getName()

    # 派生消息处理线程
    def begin_handle(self):
        self.handle_thread.start()

    def get_handle_thread(self):
        return self.handle_thread.getName()



    # 处理消息队列中的消息
    def handle_message(self):
        while not self.stop_handle:
            # 如果待处理队列为空则休息
            if self.message_queue.empty():
                time.sleep(0.01)
            else:
                # 处理消息，有开始游戏的请求以及游戏进行中的数据传输
                data, client_addr = self.message_queue.get()
                self.process_data(data, client_addr)

    # 分配消息给具体的任务
    def process_data(self, data, client_addr):
        unpack_data = unpack_client_data(data)
        print(isinstance(unpack_data, dict))
        player_id = ""
        try:
            player_id = unpack_data["id"]
        except Exception as e:
            print("数据报错误")
            print(e)
        # 开始游戏的任务
        if "begin_game" in unpack_data.keys() and unpack_data["begin_game"] == 1:
            try :
                # 注册玩家ip地址和id
                self.players_ip[player_id] = client_addr
                self.player_queue.put(player_id)

                # 如果人数足够，就开始游戏
                if self.player_queue.qsize() >= 4:
                    players = []
                    while not self.player_queue.empty() or len(players)<self.max_num:
                        players.append(self.player_queue.get())
                    cur_id = self.cur_game_id + 1

                    try:
                        cur_game = threading.Thread(target=self.begin_game,args=(players,cur_id))
                        cur_game.start()
                        self.games_threads[cur_id] = cur_game
                    except Exception as e:
                        print("游戏开始错误")
                        print(e)
            except Exception as e:
                print("数据包错误")
                print(e)
        # 向游戏发送数据
        else:
            if player_id in self.players_game.keys():
                tar_game_id = self.players_game[player_id]
                self.game_message[tar_game_id].put(unpack_data)
            else:
                pass
                # TODO：报错：错误的信息

    # 进入游戏的循环
    def begin_game(self,players,cur_id):
        """
        开始游戏线程，和游戏对象交换数据
        :param players: 加入本局游戏的玩家id
        :param data: 传入的初始化信息  ------#TODO：地图设计
        :param cur_id: 本局游戏的id
        """
        print("开始游戏", cur_id)
        self.game_message[cur_id] = Queue()
        # 最终加入游戏的玩家
        players_come_in = []
        # 添加玩家和游戏id的映射
        for pid in players:
            if self.players_game[pid]:
                #TODO 向玩家发送错误
                pass
            else:
                self.players_game[pid] = cur_id
                players_come_in.append(pid)

        # 开始游戏
        cur_game = GameCore.GameCore(cur_id)
        stop =  False
        while not stop:
            while not self.game_message[cur_id].empty():
                cur_game.input_data(self.game_message[cur_id].get())
            cur_game.gaming()
            cur_data = cur_game.output_data()
            # 处理要发送的数据的数据，即添加玩家的地址信息，然后加入发送队列
            winner = cur_data["information"][0]
            data_pack = pack_server_data(cur_data)
            for pid in players_come_in:
                self.message_queue.put((data_pack, self.players_ip[pid]))
            if winner == -1:
                stop = True
            # 控制处理速度
            time.sleep(0.015)


    # 发送待发送消息队列的数据
    def send_data(self):
        if self.server_socket is None:
            return

        while not self.stop_send:
            # 如果发送队列为空，则休息0.02秒
            if self.message_to_send.empty():
                time.sleep(0.02)
            else:
                data,addr = self.message_to_send.get()
                self.server_socket.sendto(data, addr)

    # 接收数据,将数据放入消息队列
    def receive_data(self):
        if self.server_socket is None:
            return

        while not self.stop_receive:
            data, client_addr = self.server_socket.recvfrom(2048)
            self.message_queue.put((data,client_addr))

    # 停止服务器运行
    def stop(self):
        if self.server_socket != None:
            self.stop_receive = self.stop_send = self.stop_handle = True
            stop_thread(self.receive_thread)
            print("接收线程停止")
            for t in self.games_threads:
                t.join()
            # 发送完所有消息后停止服务器
            while self.message_to_send.qsize()!=0:
                print("等待消息队列清空")
                time.sleep(1)
            self.send_thread.join()
            print("发送线程停止")
            print("处理线程停止")
            self.server_socket.close()
        else:
            print("服务器没有启动")


if __name__ == "__main__":
    my_server = Game_server()
    my_server.run("localhost",23456)
    my_server.stop()


