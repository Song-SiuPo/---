
"""
打包和解包数据
"""
'''
        预留        初始/后续    坦克数        子弹数           障碍物数       草丛数         道具数
dict = {Null:[int], Mode:[int], Numtank:[int], Numbull:[int], Numobs:[int],Numglass:[int], Numprops:[int],
                坦克序号    坦克生命            坦克子弹数       坦克杀敌数       坐标                          方向
        tanks:[{tankID:[int], tankValue:[int], tankBullet:[int], tankKill:[int], tankX:[float], tankY:[float], tankDirec:[int]},{}]
                子弹主人        子弹编号        坐标                          是否爆炸
        bulls:[ {bullerID:[int], bullID:[int], bullX:[float], bullY:[float], bullbomb:[int]}    ,{},{}]
        障碍物索引
        obs:[[x,y],      [],[]],
        草丛索引
        glass:[[x,y],    [],[]],
        道具编号            类型      状态（出现/消失） 位置
        props:[{ID:[int], Type:[int], Live:[int], X:[int], Y:[int]},      {},{}],
        安全区参数 SB为safebig    SS为safesmall
        SBX1:[], SBY1:[], SBX2:[], SBY2:[], SSX1:[], SSY1:[], SSX2:[], SSY2:[]}
'''
'''
dict = {NUM:[i,i,i,i,i,i,i],
                坦克序号    坦克生命            坦克子弹数       坦克杀敌数       方向 坐标 
        tanks:[[i,i,i,i,i,f,f],  [], []],
                子弹主人        子弹编号      是否爆炸  坐标                          
        bulls:[[i,i,i,f,f], [], []]
        障碍物索引
        obs:[[x,y],      [],[]],
        草丛索引
        glass:[[x,y],    [],[]],
        道具编号            类型      状态（出现/消失） 位置
        props:[[i,i,i,i,i], [],[]],
        安全区参数 SB为safebig    SS为safesmall
        Safe:[i,i,i,i,i,i,i,i]
        }
'''

import struct

# 打包服务器传向客户端的数据
#将一个dict转为一个包传递
#为变长dict
'''
预留        初始/后续    坦克数        子弹数           障碍物数       草丛数         道具数
dict = {num:[i,i,i,i,i,i,i],
                坦克序号    坦克生命            坦克子弹数       坦克杀敌数       方向 坐标 
        tanks:[[i,i,i,i,i,f,f],  [], []],
                子弹主人        子弹编号      是否爆炸  坐标                          
        bulls:[[i,i,i,f,f], [], []]
        障碍物索引
        obs:[[x,y],      [],[]],
        草丛索引
        glass:[[x,y],    [],[]],
        道具编号            类型      状态（出现/消失） 位置
        props:[[i,i,i,i,i], [],[]],
        安全区参数 SB为safebig    SS为safesmall
        safe:[i,i,i,i,i,i,i,i]
        }
'''
def pack_server_data(pack_dict):

    #打包第一行
    str1 = struct.pack("iiiiiii",pack_dict['num'][0],pack_dict['num'][1],pack_dict['num'][2],pack_dict['num'][3],pack_dict['num'][4],pack_dict['num'][5],pack_dict['num'][6])
    #打包第二行-Numtank
    str2 = bytes()
    for i in range(pack_dict['num'][2]):
        pstr = struct.pack("iiiiiff",pack_dict['tanks'][i][0],pack_dict['tanks'][i][1],pack_dict['tanks'][i][2],pack_dict['tanks'][i][3],pack_dict['tanks'][i][4],pack_dict['tanks'][i][5],pack_dict['tanks'][i][6])
        str2 += pstr

    #打包第三行-Numbull
    str3 = bytes()
    for i in range(pack_dict['num'][3]):
        pstr = struct.pack("iiiff",pack_dict['bulls'][i][0],pack_dict['bulls'][i][1],pack_dict['bulls'][i][2],pack_dict['bulls'][i][3],pack_dict['bulls'][i][4])
        str3 += pstr

    #打包第四行-Numobs
    str4 = bytes()
    for i in range(pack_dict['num'][4]):
        pstr = struct.pack("ii",pack_dict['obs'][i][0],pack_dict['obs'][i][1])
        str4 += pstr

    #打包第五行-Numglass
    str5 = bytes()
    for i in range(pack_dict['num'][5]):
        pstr = struct.pack("ii",pack_dict['glass'][i][0],pack_dict['glass'][i][1])
        str5 += pstr

    #打包第六行-Numprops
    str6 = bytes()
    for i in range(pack_dict['num'][6]):
        pstr = struct.pack("iiiii",pack_dict['props'][i][0],pack_dict['props'][i][1],pack_dict['props'][i][2],pack_dict['props'][i][3],pack_dict['props'][i][4])
        str6 += pstr

    #打包第七行
    str7 = struct.pack("iiiiiiii",pack_dict['safe'][0],pack_dict['safe'][1],pack_dict['safe'][2],pack_dict['safe'][3],pack_dict['safe'][4],pack_dict['safe'][5],pack_dict['safe'][6],pack_dict['safe'][7])
    #str1 = str.encode(str1)
    end_str = str1+str2+str3+str4+str5+str6+str7
    #end_str = struct.pack("sssssss",str(str1),str(str2),str(str3),str(str4),str(str5),str(str6),str(str7))
    return end_str


#服务器解包
#传过来的是打包的6个int，
# 返回一个dict
def unpack_client_data(s):
    tup = struct.unpack("iiiiii",s)
    unpack_dict = {'ID':tup[0], 'UP':tup[1], 'DOWN':tup[2], 'RIGHT':tup[3], 'LEFT':tup[4], 'FIRE':tup[5]}
    return unpack_dict


#客户端操作-解压服务器传输的包
#接受一个包
#返回为一个固定的dict
'''
预留        初始/后续    坦克数        子弹数           障碍物数       草丛数         道具数
dict = {num:[i,i,i,i,i,i,i],
                坦克序号    坦克生命            坦克子弹数       坦克杀敌数       方向 坐标 
        tanks:[[i,i,i,i,i,f,f],  [], []],
                子弹主人        子弹编号      是否爆炸  坐标                          
        bulls:[[i,i,i,f,f], [], []]
        障碍物索引
        obs:[[x,y],      [],[]],
        草丛索引
        glass:[[x,y],    [],[]],
        道具编号            类型      状态（出现/消失） 位置
        props:[[i,i,i,i,i], [],[]],
        安全区参数 SB为safebig    SS为safesmall
        safe:[i,i,i,i,i,i,i,i]
        }
'''
def unpack_server_data(end_str):
    unpack_dict = {"num":[],"tanks":[],"bulls":[],"obs":[],"glass":[],"props":[],"safe":[]}
    numstr = end_str[0:4*7]
    #safestr = end_str[-4*8,-1]
    num_tuple = struct.unpack("iiiiiii",numstr)
    for i in range(7):
        unpack_dict['num'].append( num_tuple[i])

    numtanks = unpack_dict['num'][2]
    numbulls = unpack_dict['num'][3]
    numobs = unpack_dict['num'][4]
    numglass = unpack_dict["num"][5]
    numprops = unpack_dict["num"][6]

    fmat = 'i'*7+"iiiiiff"*unpack_dict["num"][2]+"iiiff"*unpack_dict["num"][3]+"ii"*unpack_dict["num"][4]+"ii"*unpack_dict["num"][5]+"iiiii"*unpack_dict["num"][6]+"iiiiiiii"
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
    for i in range(unpack_dict["num"][4]):
        plist = [all_tuple[6+7*numtanks+5*numbulls+1+2*i],all_tuple[6+7*numtanks+5*numbulls+2+2*i]]
        unpack_dict["obs"].append(plist)
#第六行的包-道具信息-5
    #props
    for i in range(unpack_dict["num"][6]):
        plist = [all_tuple[6+7*numtanks+5*numbulls+2*numobs+2*numglass+1+5*i],all_tuple[6+7*numtanks+5*numbulls+2*numobs+2*numglass+2+5*i],all_tuple[6+7*numtanks+5*numbulls+2*numobs+2*numglass+3+5*i],all_tuple[6+7*numtanks+5*numbulls+2*numobs+2*numglass+4+5*i],all_tuple[6+7*numtanks+5*numbulls+2*numobs+2*numglass+5+5*i]]
        unpack_dict["props"].append(plist)
#第七行的包-安全区信息-8
    unpack_dict["safe"] = [all_tuple[-8],all_tuple[-7],all_tuple[-6],all_tuple[-5],all_tuple[-4],all_tuple[-3],all_tuple[-2],all_tuple[-1]]
#草丛信息-初始是传递，后续不再传递
    if unpack_dict["num"][1] == 0:#草丛列表-2
        for i in range(unpack_dict["num"][5]):
            plist = [all_tuple[6+7*numtanks+5*numbulls+2*numobs+1+2*i],all_tuple[6+7*numtanks+5*numbulls+2*numobs+2+2*i]]
            unpack_dict["glass"].append(plist)

    return unpack_dict



#客户端操作-打包客户端数据
#dict={ID:[int],UP:[int],DOWN:[int],RIGHT:[int],LEFT:[int],FIRE:[int]}
'''
输入dict={ID:1,UP:0,DOWN:1,RIGHT:0,LEFT:0，FIRE:1}
输出XXXXXXXXXXX（‘101001’）
'''
def pack_client_data(dict):
    pack_str = struct.pack("iiiiii",dict['ID'],dict['UP'],dict['DOWN'],dict['RIGHT'],dict['LEFT'],dict['FIRE'])
    return pack_str

#测试样例
server_dict = {'num':[0,0,2,1,2,1,2],
    'tanks':[[1,50,30,0,18,5.32,4.52],[2,80,40,1,108,9.32,12.52]],
    'bulls':[[1,22,0,7.7,5.5]],
    'obs':[[2,3], [8,8]],
    'glass':[[7,5]],
    'props':[[1,1,1,7,9],[2,1,1,5,6]],
    'safe':[2,2,12,12,3,3,9,9]}
s = pack_server_data(server_dict)
print("打包")
end_dict = unpack_server_data(s)
print(end_dict)


