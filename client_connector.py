'''
连接器，与服务器网络连接的类
'''


from multiprocessing import Process, Queue
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
        # self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.inqueue = Queue()
        self.outqueue = Queue()
        self.endqueue = Queue(4)
        self.process = Process(target=self._thread_main, args=(self.inqueue, self.outqueue, self.endqueue))

    def start(self):
        self.process.start()

    def end(self):
        self.endqueue.put(True)

    def _thread_main(self, inq:Queue, outq:Queue, endq:Queue):
        def listen(sock:socket.socket, outqueue, endq):
            while endq.empty():
                data = None
                try:
                    data, addr = sock.recvfrom(1024)
                except OSError as e:
                    pass
                if data:
                    outqueue.put(data)
                sleep(0.01)

        udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        end_flag = []   # 当列表不空，则发消息
        listen_th = Thread(target=listen, args=(udpsocket, outq, endq))
        listen_th.start()

        while True:
            # 准备向服务器传消息
            if not inq.empty():
                data = inq.get()
                udpsocket.sendto(data, (__class__._serverIP, __class__._serverPort))
            if not endq.empty():
                break
            sleep(0.01)

        udpsocket.close()

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
