'''
客户端的窗口主界面
'''

import tkinter as tk
from tkinter.messagebox import askyesno, showerror, showinfo
from clent_connector import Connector
from threading import Timer


class LoopTimer(Timer):
    """
    Timer的改进，可循环执行某函数
    """
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


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
        if self.playerid.get().isdigit():
            self.master.player_id = int(self.playerid.get())
            self.master.toMenuPage()
        else:
            showerror('错误', '玩家ID必须是数字')

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
        self.icon_timer = None
        self.waiting = False

    def game_wait(self):
        """
        按下"开始游戏"按钮
        """
        if not self.waiting:
            # 从主界面到开始等待匹配状态
            self.canvas.pack(padx=10, pady=5)
            self._icon_index = 0
            self.icon_timer = LoopTimer(0.1, self._change_icon)
            self.icon_timer.start()
            self.button_start.config(text='取消等待')
            self.waiting = True
            self.after(1000, self.game_start)
        else:
            # 取消当前匹配
            self.canvas.forget()
            self.icon_timer.cancel()
            self.icon_timer = None
            self.button_start.config(text='开始游戏')
            self.waiting = False

    def _change_icon(self):
        # self.after(100, self._change_icon)
        self.canvas.create_image(0, 0, anchor='nw', image=self.icons_load[self._icon_index])
        self._icon_index = (self._icon_index + 1) % 12

    def game_start(self):
        if self.waiting:
            self.game_wait()
            self.master.toGamePage()

    def exit_exe(self):
        if isinstance(self.icon_timer, LoopTimer):
            self.icon_timer.cancel()
            self.icon_timer = None


class GamePage(tk.Frame):
    """
    开始游戏后的界面
    """
    def __init__(self, master, connector, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.connect = connector
        self.canvas_main = tk.Canvas(self, width=800, height=600)
        self.canvas_main.pack(side=tk.RIGHT, padx=5, pady=5)
        self.key_down = [False for i in range(5)]  # 按键是否按下，5个分别为 W S A D 开火
        self.game_step = 0
        self.game_end = False
        self.timer = None

    def key_handler(self, event):
        """
        对按键事件的响应，持续按则持续响应
        :param event: 按键类型事件
        """
        if event.keysym == 'Up' or event.keysym.lower() == 'w':
            self.key_down[0] = True
        elif event.keysym == 'Down' or event.keysym.lower() == 's':
            self.key_down[1] = True
        elif event.keysym == 'Left' or event.keysym.lower() == 'a':
            self.key_down[2] = True
        elif event.keysym == 'Right' or event.keysym.lower() == 'd':
            self.key_down[3] = True
        elif event.keysym == 'Return' or event.keysym == 'space':
            self.key_down[4] = True

    def game_start(self):
        """
        游戏的初始化
        """
        self.game_end = False
        self.game_step = 0
        self.master.bind('<KeyPress>', self.key_handler)
        self.timer = LoopTimer(0.03, self._game)
        self.timer.start()

    def _game(self):
        if not self.game_end:
            haskeydown = False
            for key in self.key_down:
                if key:
                    haskeydown = True
                    break
            if haskeydown:
                print(self.key_down)
            self.key_down = [False for i in range(5)]
            self.game_step += 1
            if self.game_step > 300:
                self.game_end = True
        else:
            self.after(1, self.ending)

    def ending(self):
        self.timer.cancel()
        self.timer = None
        self.master.bind('<KeyPress>', None)
        showinfo('游戏结束', '游戏结束，你的击杀数为0，排名没有')
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

        self.connect = None
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

    def toGamePage(self):
        """
        转移到游戏界面
        """
        self.game_page.lift()
        self.geometry('%dx%d+%d+%d' % (900, 700, self.winfo_screenwidth() / 2 - 450,
                                  self.winfo_screenheight() / 2 - 350))

        self.cur_page = '2'
        self.after(1, self.game_page.game_start)

    def exit_win(self):
        if self.cur_page == '2':
            if askyesno("退出游戏", "游戏正在进行，确认退出当前游戏吗？"):
                self.game_page.ending()
        elif self.cur_page == '1':
            if askyesno("关闭窗口", "是否确认关闭程序？"):
                self.menu_page.exit_exe()
                self.destroy()
        else:
            self.destroy()


if __name__ == '__main__':
    mainform = MainForm()
    mainform.mainloop()
