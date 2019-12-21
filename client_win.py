'''
客户端的窗口主界面
'''

import tkinter as tk
from tkinter.messagebox import askyesno, showerror, showinfo
from client_connector import Connector
from copy import deepcopy
from ClientDisplay import ClientDisplay
from PIL import ImageTk


class LoginPage(tk.Frame):
    """
    登录的界面
    """
    def __init__(self, master, connector, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.frame1 = tk.Frame(self)
        self.frame1.pack(pady=(50, 10))
        self.frame2 = tk.Frame(self)
        self.frame2.pack(pady=10)
        self.frame3 = tk.Frame(self)
        self.frame3.pack(pady=(50, 20))

        tk.Label(self.frame1, text='用户ID').pack(side=tk.LEFT, padx=10)
        self.connect = connector
        self.playerid = tk.StringVar()
        self.entry_id = tk.Entry(self.frame1, textvariable=self.playerid)
        self.entry_id.pack(side=tk.LEFT, padx=10)

        tk.Label(self.frame2, text='密码').pack(side=tk.LEFT, padx=10)
        self.password = tk.StringVar()
        self.entry_password = tk.Entry(self.frame2, textvariable=self.password, show='*')
        self.entry_password.pack(side=tk.LEFT, padx=10)

        self.button_login = tk.Button(self.frame3, text='登录', command=self.login, width=10, height=2)
        self.button_login.pack(side=tk.LEFT, padx=(10, 20))
        self.button_regist = tk.Button(self.frame3, text='注册', command=self.regist, width=10, height=2)
        self.button_regist.pack(side=tk.LEFT, padx=(20, 10))

    def login(self):
        """
        按下登录按钮后的行为
        """
        num = self.playerid.get()
        if num.isdigit() and 0 < int(num) < (1 << 30):
            self.master.player_id = int(self.playerid.get())
            self.master.toMenuPage()
        else:
            showerror('错误', '玩家ID必须是合理范围正整数')

    def regist(self):
        pass


class MenuPage(tk.Frame):
    """
    登录后的主界面，有开始游戏按钮
    """
    def __init__(self, master, connector, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.connect = connector
        self.button_start = tk.Button(self, text='开始游戏', command=self.game_wait, width=8, height=2)
        self.button_start.pack(padx=10, pady=(20, 5))
        self.canvas = tk.Canvas(self, width=128, height=128)
        self.icons_load = [tk.PhotoImage(file='res/loading.gif', format=('gif -index %d' % i)) for i in range(12)]
        self._icon_index = 0
        self.waiting = False
        self.getinitmap = False

    def game_wait(self):
        """
        按下"开始游戏"按钮
        """
        self.getinitmap = False
        if not self.waiting:
            # 从主界面到开始等待匹配状态
            self.canvas.pack(padx=10, pady=5)
            self._icon_index = 0
            self.waiting = True
            self.button_start.config(text='取消等待')
            self.after(0, self._change_icon)
            self.after(0, self.connect.send_data_udp, {'id': self.master.player_id, 'begin_game': 1})
            self.after(0, self._try_start)
        else:
            # 取消当前匹配
            self.canvas.forget()
            self.waiting = False
            self.button_start.config(text='开始游戏')

    def _change_icon(self):
        if self.waiting:
            self.after(100, self._change_icon)
            self.canvas.create_image(0, 0, anchor='nw', image=self.icons_load[self._icon_index])
            self._icon_index = (self._icon_index + 1) % 12

    def _try_start(self):
        """
        尝试获取服务器数据，若读取到初始地图则开始游戏
        """
        if self.waiting:
            data = self.connect.get_udp_data()
            if data:
                self.connect.game_start()
                self.connect.tcp_link()
                self.after(0, self._trygetinitmap)
            else:
                self.after(5, self._try_start)

    def exit_exe(self):
        self.waiting = False

    def _trygetinitmap(self):
        if not self.getinitmap:
            self.after(5, self._trygetinitmap)
            data = self.connect.get_tcp_data()
            if data:
                self.getinitmap = True
                self.connect.tcp_unlink()
                self.game_wait()
                self.master.toGamePage(data)


class GamePage(tk.Frame):
    """
    开始游戏后的界面
    """
    def __init__(self, master, connector, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.connect = connector
        self.mapdisplay = None

        self.canvas_main = tk.Canvas(self, width=800, height=800)
        self.canvas_main.pack(padx=5, pady=5)
        self.frame1 = tk.Frame(self)
        self.frame1.pack(side=tk.BOTTOM, padx=10, pady=5)
        tk.Label(self.frame1, text='生命值').pack(side=tk.LEFT, padx=10, pady=5)
        self.label_hp = tk.Label(self.frame1, text='')
        self.label_hp.pack(side=tk.LEFT, padx=(10, 30), pady=5)
        tk.Label(self.frame1, text='子弹数').pack(side=tk.LEFT, padx=(30, 10), pady=5)
        self.label_bullet = tk.Label(self.frame1, text='')
        self.label_bullet.pack(side=tk.LEFT, padx=(10, 30), pady=5)
        tk.Label(self.frame1, text='杀敌').pack(side=tk.LEFT, padx=(30, 10), pady=5)
        self.label_kill = tk.Label(self.frame1, text='')
        self.label_kill.pack(side=tk.LEFT, padx=(10, 30), pady=5)
        tk.Label(self.frame1, text='剩余玩家').pack(side=tk.LEFT, padx=(30, 10), pady=5)
        self.rank = tk.IntVar()
        self.label_rank = tk.Label(self.frame1, textvariable=self.rank)
        self.label_rank.pack(side=tk.LEFT, padx=10, pady=5)

        self.all_map = None
        self.small_map = None
        self.player_id = 0
        self.key_down = {'Up': 0, 'Down': 0, 'Left': 0, 'Right': 0, 'fire': 0}  # 按下的按键
        self.game_end = False

    def key_handler(self, event):
        """
        对按键事件的响应，持续按则持续响应
        :param event: 按键类型事件
        """
        if event.keysym == 'Up' or event.keysym.lower() == 'w':
            self.key_down['Up'] = 1
        elif event.keysym == 'Down' or event.keysym.lower() == 's':
            self.key_down['Down'] = 1
        elif event.keysym == 'Left' or event.keysym.lower() == 'a':
            self.key_down['Left'] = 1
        elif event.keysym == 'Right' or event.keysym.lower() == 'd':
            self.key_down['Right'] = 1
        elif event.keysym == 'Return' or event.keysym == 'space':
            self.key_down['fire'] = 1

    def game_start(self, mapdata, playerid):
        """
        游戏的初始化
        """
        self.game_end = False
        self.player_id = playerid
        print(mapdata)
        self._readplayer_info(mapdata['tanks'])
        self.mapdisplay = ClientDisplay(mapdata, self.player_id)
        self.canvas_main.delete(tk.ALL)
        self.all_map = ImageTk.PhotoImage(self.mapdisplay.Draw())
        self.small_map = ImageTk.PhotoImage(self.mapdisplay.SmallMap())
        self.canvas_main.create_image(0, 0, anchor=tk.NW,
                                      image=self.all_map)
        self.canvas_main.create_image(0, 0, anchor=tk.NW,
                                      image=self.small_map)
        self.canvas_main.update()
        self.master.bind('<KeyPress>', self.key_handler)
        self.after(0, self._game)
        self.after(0, self._key_trans)

    def _game(self):
        """
        游戏30帧主循环
        """
        if not self.game_end:
            self.after(30, self._game)
            data = self.connect.get_udp_data()
            if data:
                self.mapdisplay.changedict(data)
                self.canvas_main.delete(tk.ALL)
                self.all_map = ImageTk.PhotoImage(self.mapdisplay.Draw())
                self.small_map = ImageTk.PhotoImage(self.mapdisplay.SmallMap())
                self.canvas_main.create_image(0, 0, anchor=tk.NW,
                                              image=self.all_map)
                self.canvas_main.create_image(0, 0, anchor=tk.NW,
                                              image=self.small_map)
                self.canvas_main.update()
                if 'tanks' in data:
                    self._readplayer_info(data['tanks'])
                if int(self.label_hp['text']) <= 0:
                    self.after(0, self.ending)
                elif 'info' in data and data['info'][1] >= 0 and int(self.label_hp['text']) > 0:
                    self.after(0, self.ending)
                print(data)

    def _key_trans(self):
        """
        对用户按键处理
        """
        if not self.game_end:
            keydict = deepcopy(self.key_down)
            keydict['id'] = self.player_id
            delay = 5
            for value in self.key_down.values():
                if value == 1:
                    delay = 30
                    self.connect.send_data_udp(keydict)
                    print(self.key_down)
                    break
            self.key_down = {'Up': 0, 'Down': 0, 'Left': 0, 'Right': 0, 'fire': 0}
            self.after(delay, self._key_trans)

    def _readplayer_info(self, tanks):
        '''
        传入从服务器来的坦克信息列表，更改自己的信息
        '''
        self.rank.set(len(tanks))
        for tank in tanks:
            if tank[0] == self.player_id:
                self.label_hp.config(text=tank[1])
                self.label_bullet.config(text=tank[2])
                self.label_kill.config(text=tank[3])
                break

    def ending(self):
        """
        游戏结束相关处理
        """
        self.game_end = True
        self.connect.game_end()
        self.master.bind('<KeyPress>', None)
        showinfo('游戏结束', '游戏结束，你的击杀数为%s，排名第%d' % (self.label_kill['text'], self.rank.get()))
        self.master.toMenuPage()


class MainForm(tk.Tk):
    """
    客户端主界面
    """
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title = '吃鸡版坦克大战'
        self.geometry('%dx%d+%d+%d' % (300, 300, self.winfo_screenwidth() / 2 - 150,
                                     self.winfo_screenheight() / 2 - 150))

        self.connect = Connector()
        self.connect.udpStart()
        self.player_id = 0

        self.cur_page = '0'   # '0'为登录界面，'1'为主菜单，'2'为游戏界面
        self.login_page = LoginPage(self, self.connect)
        self.menu_page = MenuPage(self, self.connect)
        self.game_page = GamePage(self, self.connect)
        self.login_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        self.menu_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        self.game_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        self.protocol("WM_DELETE_WINDOW", self.exit_win)

        self.login_page.lift()

    def toMenuPage(self):
        """
        转移到登录后的主界面
        """
        self.menu_page.lift()
        self.geometry('%dx%d+%d+%d' % (300, 300, self.winfo_screenwidth() / 2 - 150,
                                  self.winfo_screenheight() / 2 - 150))
        self.cur_page = '1'

    def toGamePage(self, mapdata):
        """
        转移到游戏界面
        """
        self.game_page.lift()
        self.geometry('%dx%d+%d+%d' % (900, 700, self.winfo_screenwidth() / 2 - 450,
                                  self.winfo_screenheight() / 2 - 350))

        self.cur_page = '2'
        self.after(0, self.game_page.game_start, mapdata, self.player_id)

    def exit_win(self):
        if self.cur_page == '2':
            if askyesno("退出游戏", "游戏正在进行，确认退出当前游戏吗？"):
                self.game_page.ending()
        elif self.cur_page == '1':
            if askyesno("关闭窗口", "是否确认关闭程序？"):
                self.menu_page.exit_exe()
                self.connect.end()
                self.destroy()
        else:
            self.connect.end()
            self.destroy()


if __name__ == '__main__':
    mainform = MainForm()
    mainform.mainloop()
