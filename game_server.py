"""
作者： mieyangyanga
文件描述：游戏服务器类
"""

import socket
import threading
import time
from queue import Queue
import GameCore
from DataTransPacks import *
from stop_thread import stop_thread
from start_map_sample import server_dict
from tcp_server import TCP_server
import copy


class Game_server():
    def __init__(self):
        # 服务器是否运行
        self.stop_send = False
        self.stop_receive = False
        self.stop_handle = False
        self.receive_info = False
        self.send_info = False
        # 服务器socket
        self.server_socket = None
        # TCP_server
        self.tcp_server = TCP_server()

        # 接受到的客户端的消息队列
        self.message_queue = Queue()
        # 要发送给客户端的消息队列，格式：(data, addr)
        self.message_to_send = Queue()
        # 等待中的玩家队列
        self.player_queue = Queue()

        # 单局最大玩家数量
        self.max_num = 10
        # 单局最小玩家数量
        self.min_num = 2

        # 玩家的id与ip的字典,接收请求开始游戏的消息时处理
        self.players_ip = {}
        # 玩家id与所在的游戏的id，开始游戏初始化时处理
        self.players_game = {}

        # 当前的游戏id
        self.cur_game_id = 10000
        # 游戏的id与对应接收消息的函数
        self.game_message = {}

        # 接收消息的线程
        self.receive_thread = threading.Thread(target=self.receive_data, args=())
        # 发送数据的线程
        self.send_thread = threading.Thread(target=self.send_data, args=())
        # 处理消息的线程
        self.handle_thread = threading.Thread(target=self.handle_message, args=())
        # 处理每局游戏的线程,格式：{id:Thread}
        self.games_threads = {}

    if "server_state":
        # 打开输出接收信息的开关
        def begin_rec_info(self):
            self.receive_info = True

        # 关闭输出
        def end_rec_info(self):
            self.receive_info = False

        # 打开输出发送信息的开关
        def begin_send_info(self):
            self.send_info = True

        # 关闭输出
        def end_send_info(self):
            self.send_info = False

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

    if "threads":
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

    if "server_function":
        # 开始游戏服务器
        def run(self, host, port = 23456):
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
            self.tcp_server.run((host, 5000))
            self.begin_receive()
            self.begin_send()
            self.begin_handle()
            # 服务器功能扩展
            print("服务器已启动")

        # 处理消息队列中的消息
        def handle_message(self):
            while not self.stop_handle:
                # 如果待处理队列为空则休息
                if self.message_queue.empty():
                    time.sleep(0.001)
                else:
                    # 处理消息，有开始游戏的请求以及游戏进行中的数据传输
                    data, client_addr = self.message_queue.get()
                    self.process_data(data, client_addr)

        # 分配消息给具体的任务
        def process_data(self, data, client_addr):
            unpack_data = unpack_client_data(data)

            player_id = ""
            try:
                player_id = unpack_data["id"]
            except Exception as e:
                print("数据包错误")
                print(e)
                return

            # 开始游戏的任务
            if "begin_game" in unpack_data.keys() and unpack_data["begin_game"] == 1:
                # 注册玩家ip地址和id
                if player_id not in self.players_ip.keys():
                    self.players_ip[player_id] = client_addr
                    self.player_queue.put(player_id)
                else:
                    self.players_ip[player_id] = client_addr
                # 如果人数足够，就开始游戏
                if self.player_queue.qsize() >= self.min_num:
                    players = []
                    while (not self.player_queue.empty()) and len(players) < self.max_num:
                        players.append(self.player_queue.get())
                    cur_id = self.cur_game_id
                    self.cur_game_id += 1
                    # 向玩家发送游戏开始消息
                    for pid in players:
                        self.message_to_send.put((str(pid).encode("utf-8"), self.players_ip[pid]))

                    # 等待客户端收到地图数据
                    time.sleep(1)
                    # 开始游戏线程
                    try:
                        cur_game = threading.Thread(target=self.begin_game,args=(players,cur_id))
                        cur_game.start()
                        self.games_threads[cur_id] = cur_game
                    except Exception as e:
                        print("游戏开始错误")
                        print(e)
            # 向游戏发送数据
            #elif "time1" in unpack_data.keys():
             #   t = time.time()*1000
              #  dct = {"time1": unpack_data["time1"],"time2":t}
               # time1 = unpack_data["time1"]
                #print("time1:",time1,t-time1)
                #data = pack_client_data(dct)
                #self.message_to_send.put((data, client_addr))
            else:
                if player_id in self.players_game.keys():
                    tar_game_id = self.players_game[player_id]
                    if tar_game_id in self.game_message and self.game_message[tar_game_id]:
                        self.game_message[tar_game_id](unpack_data)
                    #if tar_game_id in self.game_message.keys():
                        #self.game_message[tar_game_id].put(unpack_data)

        # 进入游戏的循环
        def begin_game(self,players,cur_id):
            """
            开始游戏线程，和游戏对象交换数据
            :param players: 加入本局游戏的玩家id
            :param data: 传入的初始化信息
            :param cur_id: 本局游戏的id
            """
            print("开始游戏，游戏id:", cur_id)
            # 最终加入游戏的玩家
            players_come_in = []
            # 添加玩家和游戏id的映射
            for pid in players:
                if pid in self.players_game.keys():
                    # TODO 向玩家发送错误
                    pass
                else:
                    self.players_game[pid] = cur_id
                    players_come_in.append(pid)

            # 开始游戏
            cur_game = GameCore.GameCore(cur_id)
            self.game_message[cur_id] = cur_game.input_data
            print("加入玩家", players)
            cur_game.game_init(server_dict, players)
            stop = False
            while not stop:
                winner = cur_game.gaming()
                cur_data = cur_game.output_data()
                # 处理要发送的数据的数据，即添加玩家的地址信息，然后加入发送队列
                try:
                    data_pack = pack_server_data(cur_data)
                    for pid in players_come_in:
                        self.message_to_send.put((data_pack, self.players_ip[pid]))
                except Exception as e:
                    print("打包出错")
                    print(e)
                    print(cur_data)
                # 如果有胜者产生则删除玩家所在对局并停止游戏循环
                if winner != -1:             #winner != -1:
                    stop = True
                    print("游戏结束，胜利者是", winner)
                    for player in players_come_in:
                        del self.players_game[player]
                        del self.game_message[cur_id]
                # 控制处理速度
                time.sleep(0.03)

            # 删除游戏线程记录
            del self.games_threads[cur_id]
            print("游戏",cur_id,"结束")

        # 发送待发送消息队列的数据
        def send_data(self):
            if self.server_socket is None:
                return

            while not self.stop_send:
                # 如果发送队列为空，则休息0.02秒
                if self.message_to_send.empty():
                    time.sleep(0.005)
                else:
                    data, addr = self.message_to_send.get()
                    if self.send_info:
                        try:
                            print("发送数据:",unpack_server_data(data))
                        except:
                            print("发送数据:", data.decode("utf-8"))
                    self.server_socket.sendto(data, addr)

        # 接收数据,将数据放入消息队列
        def receive_data(self):
            if self.server_socket is None:
                return

            while not self.stop_receive:
                data, client_addr = self.server_socket.recvfrom(1024)
                if self.receive_info:
                    print(unpack_client_data(data))
                self.message_queue.put((data, client_addr))

        # 停止服务器运行
        def stop(self):
            if self.server_socket:
                self.stop_receive = self.stop_send = self.stop_handle = True
                self.tcp_server.stop_fun()
                stop_thread(self.receive_thread)
                print("接收线程停止")
                for t in self.games_threads.values():
                    stop_thread(t)
                # 发送完所有消息后停止服务器
                while self.message_to_send.qsize() != 0:
                    print("等待消息队列清空")
                    time.sleep(1)
                self.send_thread.join()
                print("发送线程停止")
                print("处理线程停止")
                self.server_socket.close()
            else:
                print("服务器没有启动")

        def kill_game(self, game_id):
            if len(game_id)>0:
                game_id = game_id[0]
                if int(game_id) in self.get_games_thread().keys():
                    stop_thread(self.get_games_thread()[int(game_id)])
                    del self.get_games_thread()[int(game_id)]
                    for k,v in self.players_game:
                        if v == game_id:
                            del self.players_game[k]
                    print("游戏", game_id, "已结束")
                else:
                    print("游戏id错误")
            else:
                print("游戏id错误")


if __name__ == "__main__":
    my_server = Game_server()
    my_server.run("localhost",23456)



