"""
作者： mieyangyanga
文件描述：游戏服务器监视器
"""
from game_server import Game_server
from threading import Thread

class Moniter():
    def __init__(self):
        self.server = None
        # 指令字典
        self.command = {"begin":{    # 开始某项进程
                            "server":self.run_server,
                        },
                        "kill":{    # 停止某项进程
                            "server":self.kill,
                            "self":self.kill_self,
                            "game":self.kill_game,
                        },
                        "peak":{    # 查看某个属性
                            "server_queue":self.server_queue,
                            "game_threads":self.game_threads,
                            "server_state":self.server_state,
                        },
                        }
        self.stop = False

    # 结束某局游戏
    def kill_game(self, game_id):
        if game_id in self.server.get_games_thread().keys():
            self.server.get_games_thread()[game_id].join()
            print("游戏",game_id,"已结束")
        else:
            print("游戏id错误")

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
                print("游戏id:",k)

    def run_server(self, addr=("10.128.181.188", 23456)):
        host, port = addr
        port = int(port)
        self.server = Game_server()
        self.server.run(host, port)
        print("服务器在-",host,"-端口-",port,"上开始")

    def kill(self):
        self.server.stop()
        print("服务器结束")

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

    def get_cmd(self):
        cmd = input("请输入指令:")
        self.process_cmd(cmd)

    def moniter_run(self):
        while not self.stop:
            self.get_cmd()

    def kill_self(self):
        self.stop = True

if __name__ == "__main__":
    m = Moniter()
    m.moniter_run()

