
"""
打包和解包数据
"""


'''
字典格式说明
dict = {
'info':[i,i,i,i,i,i]    6个int---扩展、获胜者id、坦克数、子弹数、障碍物数、道具数
'tanks':[[i,i,i,i,i,f,f] ,  []] 5个int2个float为一个数组，多个数组拼凑  ---坦克id、坦克生命、坦克弹药、坦克杀敌数、方向、x、y
'bulls':[[i,i,i,f,f],   [],[]]     3个int两个float为一个数组，多个数组拼凑---子弹发射者id、子弹id、是否爆照、x、y
'obs':[[i,i] ,[i,i]]    坐标对
'props':[[i,i,i,i,i],  []]   5个int为一个数组 ---- 道具id、类型、状态、x、y
'safe':[i,i,i,i,i,i,i,i]    8个int
}
'''
'''
测试样例
server_dict = {'info':[0,0,2,1,2,1],
    'tanks':[[1,50,30,0,18,5.32,4.52],[2,80,40,1,108,9.32,12.52]],
    'bulls':[[1,22,0,7.7,5.5]],
    'obs':[[2,3], [8,8]],
    'props':[[1,1,1,7,9],[2,1,1,5,6]],
    'safe':[2,2,12,12,3,3,9,9]}
'''

import struct
import json

# 打包服务器传向客户端的数据
#将一个dict转为一个包传递
#为变长dict

def pack_server_data(pack_dict):

    #打包第一行
    str1 = struct.pack("iiiiii",pack_dict['info'][0],pack_dict['info'][1],pack_dict['info'][2],pack_dict['info'][3],pack_dict['info'][4],pack_dict['info'][5])
    #打包第二行-Numtank
    str2 = bytes()
    for i in range(pack_dict['info'][2]):
        pstr = struct.pack("iiiiiff",pack_dict['tanks'][i][0],pack_dict['tanks'][i][1],pack_dict['tanks'][i][2],pack_dict['tanks'][i][3],pack_dict['tanks'][i][4],pack_dict['tanks'][i][5],pack_dict['tanks'][i][6])
        str2 += pstr

    #打包第三行-Numbull
    str3 = bytes()
    for i in range(pack_dict['info'][3]):
        pstr = struct.pack("iiiff",pack_dict['bulls'][i][0],pack_dict['bulls'][i][1],pack_dict['bulls'][i][2],pack_dict['bulls'][i][3],pack_dict['bulls'][i][4])
        str3 += pstr

    #打包第四行-Numobs
    str4 = bytes()
    for i in range(pack_dict['info'][4]):
        pstr = struct.pack("ii",pack_dict['obs'][i][0],pack_dict['obs'][i][1])
        str4 += pstr


    #打包第六行-Numprops
    str6 = bytes()
    for i in range(pack_dict['info'][5]):
        pstr = struct.pack("iiiii",pack_dict['props'][i][0],pack_dict['props'][i][1],pack_dict['props'][i][2],pack_dict['props'][i][3],pack_dict['props'][i][4])
        str6 += pstr

    #打包第七行
    str7 = struct.pack("iiiiiiii",pack_dict['safe'][0],pack_dict['safe'][1],pack_dict['safe'][2],pack_dict['safe'][3],pack_dict['safe'][4],pack_dict['safe'][5],pack_dict['safe'][6],pack_dict['safe'][7])
    #str1 = str.encode(str1)
    end_str = str1+str2+str3+str4+str6+str7
    #end_str = struct.pack("sssssss",str(str1),str(str2),str(str3),str(str4),str(str5),str(str6),str(str7))
    return end_str


#服务器解包
def unpack_client_data(s):
    dct = json.loads(s)
    return dct


#客户端操作-解压服务器传输的包
#接受一个包
#返回为一个固定的dict

def unpack_server_data(end_str):
    unpack_dict = {"info":[],"tanks":[],"bulls":[],"obs":[],"props":[],"safe":[]}
    numstr = end_str[0:4*6]
    #safestr = end_str[-4*8,-1]
    num_tuple = struct.unpack("iiiiii",numstr)
    for i in range(6):
        unpack_dict['info'].append( num_tuple[i])

    numtanks = unpack_dict['info'][2]
    numbulls = unpack_dict['info'][3]
    numobs = unpack_dict['info'][4]
    numprops = unpack_dict["info"][5]

    fmat = 'i'*6+"iiiiiff"*unpack_dict["info"][2]+"iiiff"*unpack_dict["info"][3]+"ii"*unpack_dict["info"][4]+"iiiii"*unpack_dict["info"][5]+"iiiiiiii"
    all_tuple = struct.unpack(fmat,end_str)

#第一行的包- 计数和Mode

#第二行的包-坦克信息-7
    for i in range(numtanks):
        plist = [all_tuple[6+1+7*i],all_tuple[6+2+7*i],all_tuple[6+3+7*i],all_tuple[6+4+7*i],all_tuple[6+5+7*i],all_tuple[6+6+7*i],all_tuple[6+7+7*i]]
        unpack_dict["tanks"].append(plist)
#第三行的包-子弹信息-5
    for i in range(numbulls):
        plist = [all_tuple[6+7*numtanks+1+5*i],all_tuple[6+7*numtanks+2+5*i],all_tuple[6+7*numtanks+3+5*i],all_tuple[6+7*numtanks+4+5*i],all_tuple[6+7*numtanks+5+5*i]]
        unpack_dict["bulls"].append(plist)
#第四行的包-障碍物信息-2
    for i in range(numobs):
        plist = [all_tuple[6+7*numtanks+5*numbulls+1+2*i],all_tuple[6+7*numtanks+5*numbulls+2+2*i]]
        unpack_dict["obs"].append(plist)
#第六行的包-道具信息-5
    #props
    for i in range(numprops):
        plist = [all_tuple[6+7*numtanks+5*numbulls+2*numobs+1+5*i],all_tuple[6+7*numtanks+5*numbulls+2*numobs+2+5*i],all_tuple[6+7*numtanks+5*numbulls+2*numobs+3+5*i],all_tuple[6+7*numtanks+5*numbulls+2*numobs+4+5*i],all_tuple[6+7*numtanks+5*numbulls+2*numobs+5+5*i]]
        unpack_dict["props"].append(plist)
#第七行的包-安全区信息-8
    unpack_dict["safe"] = [all_tuple[-8],all_tuple[-7],all_tuple[-6],all_tuple[-5],all_tuple[-4],all_tuple[-3],all_tuple[-2],all_tuple[-1]]


    return unpack_dict



def pack_client_data(dict):
    pack_str = json.dumps(dict)
    return pack_str

if __name__ == "__main__":
#测试样例
    server_dict = {'info':[0,0,2,1,2,1],
    'tanks':[[1,50,30,0,18,5.32,4.52],[2,80,40,1,108,9.32,12.52]],
    'bulls':[[1,22,0,7.7,5.5]],
    'obs':[[2,3], [8,8]],
    'props':[[1,1,1,7,9],[2,1,1,5,6]],
    'safe':[2,2,12,12,3,3,9,9]}
    s = pack_server_data(server_dict)
    print("打包")
    end_dict = unpack_server_data(s)
    print(end_dict)


