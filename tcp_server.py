"""
作者： mieyangyanga
文件描述：游戏tcp服务器类
"""

import socket
from queue import Queue
from threading import Thread,currentThread
import json
from start_map_sample import server_dict
from stop_thread import stop_thread


class TCP_server():
    def __init__(self):
        self.socket = None
        self.stop = False

        # 监听端口是否有链接的线程
        self.lsn_to_thread = Thread(target=self.listen_to_accept, args=())
        # 当前派生出的线程
        self.process_threads = {}

    # 运行tcp服务器
    # 端口号：5000
    def run(self, addr=("127.0.0.1", 5000)):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(addr)
            self.socket.listen(32)
            print("tcp服务器在-", addr[0], "-端口-", addr[1], "上开始")
        except Exception as e:
            print("绑定tcp端口失败")
            raise e

        self.lsn_to_thread.start()

    def stop_fun(self):
        stop_thread(self.lsn_to_thread)
        for k,v in self.process_threads:
            v.join()
        self.socket.close()

    def listen_to_accept(self):
        while not self.stop:
            s, addr = self.socket.accept()
            print("接受到tcp请求")
            cur_thread = Thread(target=self.tcp_link, args=(s, ))
            cur_thread.start()
            self.process_threads[cur_thread.ident] = cur_thread

    # 处理一个tcp请求
    def tcp_link(self, s):
        # 第一个包是接下来数据包的长度
        # length = int(s.recv(1024))
        # cur_len = 0
        # data = ""
        # while cur_len < length:
        #     cur_data = s.recv(1024)
        #     cur_len += len(cur_data)
        #     data += cur_data

        # try:
        #     dct = json.loads(data.decode('utf-8'))
        #     self.process_cmd(s, dct)
        # except Exception as e:
        #     print("数据包解析错误")
        #     print(e)
        data = json.dumps(server_dict).encode("utf-8")
        length = len(data)
        s.send(str(length).encode("utf-8"))
        s.send(data)
        s.close()
        del self.process_threads[currentThread().ident]

    # 处理接收到的请求
    def process_cmd(self, s, dct):
        if "begin_game" in dct.keys() and dct["begin_game"] == 1:
            data = json.dumps(server_dict).encode("utf-8")
            length = len(data)
            s.send(length)
            s.send(data)
        else:
            pass


if __name__ == "__main__":
    t = TCP_server()
    t.run()
    t.stop_fun()
