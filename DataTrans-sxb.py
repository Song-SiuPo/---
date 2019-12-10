
"""
打包和解包数据
"""
'''
        预留        初始/后续    坦克数        子弹数           障碍物数       草丛数         道具数
dict = {Null:[char], Mode:[int], Numtank:[int], Numbull:[int], Numobs:[int],Numglass:[int], Numprops:[int],
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


import struct

# 打包服务器传向客户端的数据
#将一个dict转为一个包传递
#由于为变长dict
#则按行分别打包，将包再并未一个包传递，相当于打了两层，接受时再逐层拆分
def pack_server_data(dict):

    #打包第一行
    str1 = struct.pack("ciiiiii",dict["Null"],dict["Mode"],dict["Numtank"],dict["Numbull"],dict["Numobs"],dict["Numglass"],dict["Numprops"])
    #打包第二行-Numtank
    str2 = ''
    for i in range(dict["Numtank"]):
        pstr = struct.pack("iiiiffi",dict["tanks"][i]["tankID"],dict["tanks"][i]["tankValue"],dict["tanks"][i]["tankBullet"],dict["tanks"][i]["tankKill"],dict["tanks"][i]["tankX"],dict["tanks"][i]["tankY"],dict["tanks"][i]["tankDirec"])
        str2 = '+'+pstr
    str2 = str2[1:]
    #打包第三行-Numbull
    str3 = ''
    for i in range(dict["Numbull"]):
        pstr = struct.pack("iiffi",dict["bulls"][i]["bullerID"],dict["bulls"][i]["bullID"],dict["bulls"][i]["bullX"],dict["bulls"][i]["bullY"],dict["bulls"][i]["bullBomb"])
        str3 = '+'+pstr
    str3 = str3[1:]
    #打包第四行-Numobs
    str4 = ''
    for i in range(dict["Numobs"]):
        pstr = struct.pack("ii",dict["obs"][i][0],dict["obs"][i][1])
        str4 = '+'+pstr
    str4 = str4[1:]
    #打包第五行-Numglass
    str5 = ''
    for i in range(dict["Numglass"]):
        pstr = struct.pack("ii",dict["glass"][i][0],dict["glass"][i][1])
        str5 = '+'+pstr
    str5 = str5[1:]
    #打包第六行-Numprops
    str6 = ''
    for i in range(dict["Numprops"]):
        pstr = struct.pack("iiiii",dict["props"][i]["ID"],dict["props"][i]["Type"],dict["props"][i]["Live"],dict["props"][i]["X"],dict["props"][i]["Y"])
        str6 = '+'+pstr
    str6 = str6[1:]
    #打包第七行
    str7 = struct.pack("iiiiiiii",dict["SBX1"],dict["SBY1"],dict["SBX2"],dict["SBY2"],dict["SSX1"],dict["SSY1"],dict["SSX2"],dict["SSY2"])
    str = struct.pack("sssssss",str1,str2,str3,str4,str5,str6,str7)
    return str


#服务器解包
#传过来的是打包的6个int，
# 返回一个dict
def unpack_client_data(s):
    tup = struct.unpack("iiiiii",s)
    dict = {'ID':tup[0], 'UP':tup[1], 'DOWN':tup[2], 'RIGHT':tup[3], 'LEFT':tup[4], 'FIRE':tup[5]}
    return dict


#客户端操作-解压服务器传输的包
#接受一个包
#返回为一个固定的dict
def unpack_server_data(s):
    #总包拆分
    tup = struct.unpack("sssssss",s)
    str1 = tup[0]#第一行的包
    str2 = tup[1]
    str3 = tup[2]
    str4 = tup[3]
    str5 = tup[4]
    str6 = tup[5]
    str7 = tup[6]#第七行的包
#第一行的包- 计数和Mode
    tup1 = struct.pack("ciiiiii",str1)
    dict["Mode"] = tup1[1]
    dict["Numtank"] = tup1[2]
    dict["Numbull"] = tup1[3]
    dict["Numobs"] = tup1[4]
    dict["Numglass"] = tup1[5]
    dict["Numprops"] = tup1[6]
#第二行的包-坦克信息
    for i in range(dict["Numtank"]):
        tup2 = struct.unpack("iiiiffi",str2.split('+')[i])
        dict2 = {"tankID":tup2[0], "tankValue":tup2[1], "tankBullet":tup2[2], "tankKill":tup2[3], "tankX":tup2[4], "tankY":tup2[5], "tankDirec":tup2[6]}
        dict["tanks"].append(dict2)
#第三行的包-子弹信息
    for i in range(dict["Numbull"]):
        tup3 = struct.unpack("iiffi",str3.split('+')[i])
        dict3 = {"bullerID":tup3[0], "bullID":tup3[1], "bullX":tup3[2], "bullY":tup3[3], "bullbomb":tup3[4]}
        dict["bulls"].append(dict3)
#第四行的包-障碍物信息
    for i in range(dict["Numobs"]):
        tup4 = struct.unpack("ii",str4.split('+')[i])
        list = [tup4[0],tup4[1]]
        dict["obs"].append(list)
#第六行的包-道具信息
    #props
    for i in range(dict["Numprops"]):
        tup6 = struct.unpack("iiiii",str6.split('+')[i])
        dict6 = {"ID":tup6[0],"Type":tup6[1],"Live":tup6[2],"X":tup6[3],"Y":tup6[4]}
        dict["props"].append(dict6)
#第七行的包-安全区信息
    tup7 = struct.unpack("iiiiiiii",str7)
    dict["SBX1"] = tup7[0]
    dict["SBY1"] = tup7[1]
    dict["SBX2"] = tup7[2]
    dict["SBY2"] = tup7[3]
    dict["SSX1"] = tup7[4]
    dict["SSY1"] = tup7[5]
    dict["SSX2"] = tup7[6]
    dict["SSY2"] = tup7[7]
#草丛信息-初始是传递，后续不再传递
    if dict["Mode"] == 0:#草丛列表
        for i in range(dict["Numglass"]):
            tup5 = struct.unpack("ii", str5.split('+')[i])
            list = [tup5[0], tup5[1]]
            dict["glass"].append(list)

    return dict



#客户端操作-打包客户端数据
#dict={ID:[int],UP:[int],DOWN:[int],RIGHT:[int],LEFT:[int],FIRE:[int]}
'''
输入dict={ID:1,UP:0,DOWN:1,RIGHT:0,LEFT:0，FIRE:1}
输出XXXXXXXXXXX（‘101001’）
'''
def pack_client_data(dict):
    str = struct.pack("iiiiii",dict['ID'],dict['UP'],dict['DOWN'],dict['RIGHT'],dict['LEFT'],dict['FIRE'])
    return str



