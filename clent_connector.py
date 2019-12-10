'''
连接器，与服务器网络连接的类
'''


import socket
import pack_data as pac


class Connector:
    serverIP = '127.0.0.1'
    serverPort = 1080
    def __init__(self):
        self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpsocket.connect((__class__.serverIP, __class__.serverPort))
        self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __del__(self):
        self.tcpsocket.close()
        self.udpsocket.close()

    def send_data_tcp(self, diction):
        binary = pac.pack_client_data(diction)
        self.tcpsocket.send(binary)

    def send_data_udp(self, diction):
        binary = pac.pack_client_data(diction)
        self.udpsocket.sendto(binary, (__class__.serverIP, __class__.serverPort))

    def get_tcp_data(self):
        # 接收tcp的信息
        buffer = []
        while True:
            # 每次最多接收64k字节:
            d = self.tcpsocket.recv(65536)
            if d:
                buffer.append(d)
            else:
                break
        return pac.unpack_server_data(b''.join(buffer))

    def get_udp_data(self):
        # 接收udp的信息
        buffer = []
        while True:
            # 每次最多接收64k字节:
            d, add = self.udpsocket.recvfrom(65536)
            if add == (__class__.serverIP, __class__.serverPort) and d:
                buffer.append(d)
            else:
                break
        return pac.unpack_server_data(b''.join(buffer))


