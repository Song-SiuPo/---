
"""
打包和解包数据
"""

import struct



# 打包服务器传向客户端的数据
def pack_server_data(data, mode):
    """
    打包服务器传向客户端的数据
    :param data:list 要打包的数据，格式：[[数据1],[数据2]...[]]
    :param mode: 打包模式, '0'代表初始发往客户端的包，'1'代表游戏进行过程中发往客户端的包, ...
    :return: 打包后的数据
    """
    pass

def unpack_server_data(data):
    pass

def pack_client_data(data):
    pass

def unpack_client_data(data):
    pass