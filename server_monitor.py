"""
作者： mieyangyanga
文件描述：游戏服务器监视器
"""
from game_server import Game_server
from threading import Thread
import copy
from tcp_server import TCP_server
from stop_thread import stop_thread
import time


class Monitor:
    def __init__(self):
        self.server = None
        # 指令字典
        self.command = {"begin": {    # 开始某项进程
                            "server": self.run_server,
                            "all":self.run
                        },
                        "restart": {
                            "server": self.restart,
                        },
                        "kill": {    # 停止某项进程
                            "server": self.kill,
                            "self": self.kill_self,
                            "game": self.kill_game,
                        },
                        "peek": {    # 查看某个属性
                            "server_queue": self.server_queue,
                            "game_threads": self.game_threads,
                            "server_state": self.server_state,
                            "players_queue": self.players_queue,
                        },
                        "monitor": {
                            "receive":  self.monitor_receive,
                            "send":  self.monitor_send,
                            "all": self.monitor_all
                        },
                        "stop": {
                            "receive": self.stop_receive,
                            "send": self.stop_send
                        }
                        }
        self.stop = False

    if "monitor":

        def monitor_all(self, time = None):
            self.monitor_receive(time)
            self.monitor_send(time)

        def monitor_receive(self, time = None):
            print("开始监听接收数据")
            self.server.begin_rec_info()
            if time:
                time.sleep(time)
                self.stop_receive()

        def monitor_send(self, time = None):
            print("开始监听发送的数据")
            self.server.begin_send_info()
            if time:
                time.sleep(time)
                self.stop_send()

    if "stop":
        def stop_receive(self):
            self.server.end_rec_info()

        def stop_send(self):
            print("stop send")
            self.server.end_send_info()

    if "peek":
        def players_queue(self):
            print("等待队列中的玩家：")
            plays = copy.copy(self.server.get_players_in_queue())
            cnt = 0
            while not plays.empty():
                cnt += 1
                cur_player = plays.get()
                print(cur_player)
            print("共有",cnt,"位玩家在等待")

        def server_state(self):
            print("游戏服务器运行中的线程：")
            print("接收线程：")
            print(self.server.get_receive_thread())
            print("发送线程：")
            print(self.server.get_send_thread())
            print("处理线程：")
            print(self.server.get_handle_thread())
            self.game_threads()

        def server_queue(self):
            length = self.server.get_message_send_len()
            print("服务器待发送队列长度为：",length)

        def game_threads(self):
            print("服务器游戏线程信息：")
            threads = self.server.get_games_thread()
            if threads == {}:
                print("没有正在运行的游戏")
            else:
                for k,v in threads.items():
                    print("游戏id:", k)

    def restart(self):
        self.kill_self()
        time.sleep(1)
        self.run()

    if "begin":
        def run_server(self, addr=("127.0.0.1", 23456)):
            host, port = addr
            port = int(port)
            self.server = Game_server()
            self.server.run(host, port)
            print("游戏服务器在-", host, "-端口-", port, "上开始")

        def run(self, addr=("127.0.0.1", 23456)):
            self.run_server(addr)
            self.monitor_all()

    if "kill":
        def kill(self):
            if self.server:
                self.server.stop()
                print("服务器结束")

        # 结束某局游戏
        def kill_game(self, game_id):
            self.server.kill_game(game_id)

        def kill_self(self):
            self.stop = True

    if "self":
        # 处理命令语句
        def process_cmd(self, cmd):
            words = cmd.split(" ")
            if len(words)<=1:
                return
            try:
                if len(words)>2:
                    self.command[words[0]][words[1]](tuple(words[2:]))
                else:
                    self.command[words[0]][words[1]]()
            except Exception as e:
                print("输入的命令错误")
                print(e)

        # 获取处理指令
        def get_cmd(self):
            cmd = input(">>>")
            t = Thread(target=self.process_cmd, args=(cmd,))
            t.start()

        def monitor_run(self):
            while not self.stop:
                self.get_cmd()

            # 服务器结束
            self.kill()
            print("服务器停止")


if __name__ == "__main__":
    m = Monitor()
    m.monitor_run()
    #m.run_server()

