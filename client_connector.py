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
    _serverPort = 23456

    def __init__(self):
        # self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.tcpsocket.connect((__class__._serverIP, __class__._serverPort))
        self.inqueue = Queue()
        self.outqueue = Queue()
        self.end_flag = False
        self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpsendth = Thread(target=self._thread_udpsend)
        self.udplistenth = Thread(target=self._thread_udplisten)

    def start(self):
        self.udpsendth.start()
        self.udplistenth.start()

    def end(self):
        self.end_flag = True
        self.udpsocket.close()

    def _thread_udpsend(self):
        while not self.end_flag:
            # 准备向服务器传消息
            if not self.inqueue.empty():
                data = self.inqueue.get()
                self.udpsocket.sendto(data, (__class__._serverIP, __class__._serverPort))
            sleep(0.01)

    def _thread_udplisten(self):
        while not self.end_flag:
            data = None
            try:
                data, addr = self.udpsocket.recvfrom(1024)
            except OSError as e:
                if e.errno == 10022 or e.errno == 10038:
                    break
                raise e
            if data:
                self.outqueue.put(data)
            sleep(0.01)

    '''
    def send_data_tcp(self, diction):
        binary = pac.pack_client_data(diction)
        self.tcpsocket.send(binary)
    '''
    def send_data_udp(self, diction):
        binary = pac.pack_client_data(diction)
        self.inqueue.put(binary)
    '''
    def get_tcp_data(self):
        # 接收tcp的信息
        buffer = []
        while True:
            # 每次最多接收64k字节:
            d = self.tcpsocket.recv(1024)
            if d:
                buffer.append(d)
            else:
                break
        return pac.unpack_server_data(b''.join(buffer))
    '''
    def get_udp_data(self):
        # 接收udp的信息
        if not self.outqueue.empty():
            binary = self.outqueue.get()
            return pac.unpack_server_data(binary)
        return None
