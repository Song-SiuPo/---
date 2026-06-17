'''
连接器，与服务器网络连接的类
'''


from queue import Queue
from threading import Thread
from time import sleep
import socket
import DataTransPacks as pac


# 套接字的良性错误：未绑定/已关闭/被中断/连接重置/未连接等，出现时忽略即可，不应让监听线程崩溃。
# Windows下Winsock的错误码在 e.winerror（如10022），而 e.errno 是被映射后的POSIX值（如22），两者都要认。
_BENIGN_WSA = {10004, 10009, 10022, 10038, 10053, 10054, 10057}
_BENIGN_ERRNO = {4, 9, 22, 103, 104, 107}


def _is_benign_sockerr(e):
    return getattr(e, 'winerror', None) in _BENIGN_WSA or e.errno in _BENIGN_ERRNO


class Connector:
    _serverIP = '127.0.0.1'
    _udpPort = 23456
    _tcpPort = 5000

    def __init__(self):
        self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 显式绑定本地端口，否则在Windows上发首包前直接recvfrom会抛WinError 10022
        self.udpsocket.bind(('', 0))
        self.inqueue_udp = Queue()
        self.outqueue_udp = Queue()
        self.inqueue_tcp = Queue()
        self.outqueue_tcp = Queue()
        self.end_flag = False
        self.map_init = False
        self.tcp_start = False
        self.tcp_listening = False
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
        self.tcp_listening = True
        if not self.tcp_start:
            self.tcplistenth.start()
            self.tcpsendth.start()
            self.tcp_start = True

    def tcp_unlink(self):
        self.tcp_listening = False
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
                if not _is_benign_sockerr(e):
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
            # 仅在握手期间（tcp_link~tcp_unlink）监听，避免对未连接socket空转抢GIL
            if not self.tcp_listening:
                sleep(0.05)
                continue
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
                if not _is_benign_sockerr(e):
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

    def get_tcp_data(self):
        # 接收tcp的信息
        if not self.outqueue_tcp.empty():
            return self.outqueue_tcp.get()
        return None

    def get_udp_data(self):
        # 接收udp的信息
        if not self.outqueue_udp.empty():
            return self.outqueue_udp.get()
        return None
