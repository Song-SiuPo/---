'''
连接器，与服务器网络连接的类
'''


from multiprocessing import Queue
from threading import Thread
from time import sleep
import socket
import DataTransPacks as pac


class Connector:
    _serverIP = '10.128.181.188'
    _udpPort = 23456
    _tcpPort = 5000

    def __init__(self):
        self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.inqueue_udp = Queue()
        self.outqueue_udp = Queue()
        self.inqueue_tcp = Queue()
        self.outqueue_tcp = Queue()
        self.end_flag = False
        self.map_init = False
        self.tcp_start = False
        self.udpsendth = Thread(target=self._thread_udpsend)
        self.udplistenth = Thread(target=self._thread_udplisten)
        self.tcpsendth = Thread(target=self._thread_tcpsend)
        self.tcplistenth = Thread(target=self._thread_tcplisten)

    def game_start(self):
        self.map_init = True

    def game_end(self):
        self.map_init = False

    def udpStart(self):
        self.udpsendth.start()
        self.udplistenth.start()

    def end(self):
        self.end_flag = True
        self.udpsocket.close()

    def tcp_link(self):
        self.tcpsocket.connect((__class__._serverIP, __class__._tcpPort))
        if not self.tcp_start:
            self.tcplistenth.start()
            self.tcpsendth.start()
            self.tcp_start = True

    def tcp_unlink(self):
        self.tcpsocket.shutdown(2)
        self.tcpsocket.close()
        self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def _thread_udpsend(self):
        while not self.end_flag:
            # 准备向服务器传消息
            if not self.inqueue_udp.empty():
                data = self.inqueue_udp.get()
                self.udpsocket.sendto(data, (__class__._serverIP, __class__._udpPort))
            sleep(0.005)

    def _thread_udplisten(self):
        while not self.end_flag:
            data = None
            try:
                data, addr = self.udpsocket.recvfrom(32768)
            except OSError as e:
                if e.errno != 10022 and e.errno != 10038:
                    raise e
            if data:
                # 渲染压力过大，清除无用帧信息
                if self.outqueue_udp.qsize() > 5:
                    while not self.outqueue_udp.empty():
                        self.outqueue_udp.get()
                if self.map_init:
                    self.outqueue_udp.put(pac.unpack_server_data(data))
                else:
                    self.outqueue_udp.put(pac.unpack_client_data(data))
            sleep(0.005)

    def _thread_tcpsend(self):
        while not self.end_flag:
            # 准备向服务器传消息
            if not self.inqueue_tcp.empty():
                data = self.inqueue_tcp.get()
                self.tcpsocket.send(data)
            sleep(0.005)

    def _thread_tcplisten(self):
        while not self.end_flag:
            data = None
            try:
                if self.map_init:
                    data = int(self.tcpsocket.recv(1024).decode('utf-8'))
                    buffer = b""
                    while len(buffer) < data:
                        buffer += self.tcpsocket.recv(1024)
                    data = pac.unpack_client_data(buffer)
                else:
                    data = self.tcpsocket.recv(32768)
            except OSError as e:
                if e.errno != 10057 and e.errno != 10038:
                    raise e
            if data:
                self.outqueue_tcp.put(data)
            sleep(0.005)

    def send_data_tcp(self, diction):
        binary = pac.pack_client_data(diction)
        self.inqueue_tcp.put(binary)

    def send_data_udp(self, diction):
        binary = pac.pack_client_data(diction)
        self.inqueue_udp.put(binary)
        print("发送", self.inqueue_udp.qsize())

    def get_tcp_data(self):
        # 接收tcp的信息
        if not self.outqueue_tcp.empty():
            return self.outqueue_tcp.get()
        return None

    def get_udp_data(self):
        # 接收udp的信息
        if not self.outqueue_udp.empty():
            print("接收", self.outqueue_udp.qsize())
            return self.outqueue_udp.get()
        return None
