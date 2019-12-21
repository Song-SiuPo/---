#客户端可视化函数
#输出为客户端显示截图
from PIL import Image, ImageDraw, ImageFont

# 地图初始化字典默认可以自动读取
Mapdict = {
    'info': [0, 0, 1, 1, 2, 0, 2],
    'tanks': [[1, 2, 3, 4, 40, 6, 7], [1, 2, 3, 4, 40, 0, 1]],
    'bulls': [[1, 1, 1, 7, 7]],
    'obs': [[1, 1], [4, 4]],
    'props': [],
    'safe': [1, 1, 80, 80, 10, 10, 60, 60],
    'glass': [[0, 0], [5, 5]]
}
Nowdict = Mapdict


# 获胜情况交给其他部分判断-只处理未获胜情况
def Display(ChangeDict):  # 默认21*21
    # 计算Nowdict
    #

    Nowdict['info'][2] = ChangeDict['info'][2]  # tanks
    Nowdict['info'][3] = ChangeDict['info'][3]  # bulls
    # Nowdict['info'][5] = ChangeDict['info'][5]#props
    # Nowdict['info'][6] = ChangeDict['info'][6]草丛-不用管

    Nowdict['tanks'] = ChangeDict['tanks']
    Nowdict['bulls'] = ChangeDict['bulls']
    Nowdict['safe'] = ChangeDict['safe']
    # 障碍物剔除
    for i in range(ChangeDict['info'][4]):
        for j in range(Nowdict['info'][4]):
            if Nowdict['obs'][j] == ChangeDict['obs'][i]:
                Nowdict['obs'].pop(j)
                break

    Nowdict['info'][4] = Nowdict['info'][4] - ChangeDict['info'][4]  # obs

    # 道具
    for i in range(ChangeDict['info'][5]):
        if ChangeDict['props'][i][2] == 0:  # 消失
            for j in range(Nowdict['info'][5]):
                if Nowdict['props'][j][3] == ChangeDict['props'][i][3] \
                        and Nowdict['props'][j][4] == ChangeDict['props'][i][4]:
                    Nowdict['props'].pop(j)
                    break
        else:  # 出现
            Nowdict['props'].append(ChangeDict['props'][i])
    for i in range(ChangeDict['info'][5]):
        if ChangeDict['props'][i][2] == 0:  # 消失
            Nowdict['info'][5] = Nowdict['info'][5] - 1
        else:  # 出现
            Nowdict['info'][5] = Nowdict['info'][5] + 1
    #
    return Nowdict


# 贴图显示
def DisplayImg(Nowdict, ID):
    img_back = Image.open(r"D:\CodingDATA\tankpic\backONE.png")
    img_glass = Image.open(r"D:\CodingDATA\tankpic\glass.png")
    img_obs = Image.open(r"D:\CodingDATA\tankpic\obs.png")
    img_bull = Image.open(r"D:\CodingDATA\tankpic\bull.png")
    img_bullbomb = Image.open(r"D:\CodingDATA\tankpic\bullbomb.png")
    img_othertank = Image.open(r"D:\CodingDATA\tankpic\othertank.png")
    img_safe = Image.open(r"D:\CodingDATA\tankpic\safe.png")
    img_selftank = Image.open(r"D:\CodingDATA\tankpic\selftank.png")
    img_drug = Image.open(r"D:\CodingDATA\tankpic\drug.png")
    img_ammo = Image.open(r"D:\CodingDATA\tankpic\ammo.png")
    #
    selfX = Nowdict['tanks'][ID - 1][5]
    selfY = Nowdict['tanks'][ID - 1][6]
    if selfX < 10 or selfX > 90 or selfY < 10 or selfY > 90:
        if selfX < 10:
            X = selfX
        elif selfX > 90:
            X = 10 + (selfX - 90)
        else:
            X = 10
        if selfY < 10:
            Y = selfY
        elif selfY > 90:
            Y = 10 + (selfY - 90)
        else:
            Y = 10

    else:  # 正常情况
        X = 10
        Y = 10
    # 得到了XY，开始贴图
    # 贴自己
    img_s = img_selftank.rotate(Nowdict['tanks'][ID - 1][4])
    img_back.paste(img_s, (X * 50, Y * 50))
    # 贴障碍物
    for i in range(Nowdict['info'][4]):
        thingX = Nowdict['obs'][i][0] - selfX + X
        thingY = Nowdict['obs'][i][1] - selfY + Y
        if thingX < 21 and thingY < 21:
            img_back.paste(img_obs, (thingX * 50, thingY * 50))
    # 贴草丛
    for i in range(Nowdict['info'][6]):
        thingX = Nowdict['glass'][i][0] - selfX + X
        thingY = Nowdict['glass'][i][1] - selfY + Y
        if thingX < 21 and thingY < 21:
            img_back.paste(img_glass, (thingX * 50, thingY * 50))
    # 贴道具
    for i in range(Nowdict['info'][5]):
        thingX = Nowdict['props'][i][3] - selfX + X
        thingY = Nowdict['props'][i][4] - selfY + Y
        if thingX < 21 and thingY < 21:
            if Nowdict['props'][i][1] == 0:  # 加血
                img_back.paste(img_drug, (thingX * 50, thingY * 50))
            else:  # 加子弹
                img_back.paste(img_ammo, (thingX * 50, thingY * 50))
    # 贴子弹
    for i in range(len(Nowdict['bulls'])):
        thingX = Nowdict['bulls'][i][3] - selfX + X  # 浮点数！！！
        thingY = Nowdict['bulls'][i][4] - selfY + Y
        if thingX < 21 and thingY < 21:
            if Nowdict['bulls'][i][2] == 0:  # 正常
                img_back.paste(img_bull, (thingX * 50, thingY * 50))
            else:  # 加子弹
                img_back.paste(img_bullbomb, (thingX * 50, thingY * 50))
    # 贴安全区

    # 贴其他坦克
    for i in range(len(Nowdict['tanks'])):
        thingX = Nowdict['tanks'][i][5] - selfX + X
        thingY = Nowdict['tanks'][i][6] - selfY + Y
        if thingX < 21 and thingY < 21:
            if (i != (ID - 1)) and (InGlass(i + 1, Nowdict) == False):
                img_back.paste(img_othertank, (thingX * 50, thingY * 50))
    # 贴血量、id、子弹数、杀敌数
    text = 'ID:' + str(ID) + '   LifeValue:' + str(Nowdict['tanks'][ID - 1][1]) + '   Bulls:' + str(
        Nowdict['tanks'][ID - 1][2]) + '   Kills:' + str(Nowdict['tanks'][ID - 1][3])
    draw = ImageDraw.Draw(img_back)
    font = ImageFont.truetype("consola.ttf", 13, encoding="unic")  # 设置字
    draw.text((0, 540), text, 'fuchsia', font)

    return img_back


# 判断坦克是否在草丛里
def InGlass(tankID, Nowdict):
    judge = False
    for i in range(len(Nowdict['glass'])):
        if Nowdict['tanks'][tankID - 1][5] == Nowdict['glass'][i][0] and Nowdict['tanks'][tankID - 1][6] == \
                Nowdict['glass'][i][1]:
            judge = True
    return judge


# 输出小地图
def SmallMap(tankID, Nowdict):
    img_smap = Image.open(r"D:\CodingDATA\tankpic\smallmap.png")
    selfX = Nowdict['tanks'][tankID - 1][5]
    selfY = Nowdict['tanks'][tankID - 1][6]
    draw = ImageDraw.Draw(img_smap)
    draw.rectangle((Nowdict['safe'][0], Nowdict['safe'][1], Nowdict['safe'][2], Nowdict['safe'][3]), 'yellow')
    draw.rectangle((Nowdict['safe'][4], Nowdict['safe'][5], Nowdict['safe'][6], Nowdict['safe'][7]), 'green')
    # draw.line((selfX,selfY,selfX+1,selfY+1),'red')
    draw.ellipse((selfX - 2, selfY - 2, selfX + 2, selfY + 2), 'red')
    return img_smap


# dict更新函数
# def Display(ChangeDict)/输入变动的dict，生成新的总的dict
# 先调用此函数，生成新的dict

# 主界面显示函数
# DisplayImg(Nowdict, ID)/输入总的dict及当前ID

# 生成图片

# 小地图显示函数
# SmallMap(1,Mapdict)
img3 = DisplayImg(Mapdict, 1)
img3.show()
