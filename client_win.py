'''
客户端的窗口主界面
'''

import tkinter as tk
from clent_connector import Connector
from threading import Thread, Timer


class LoopTimer(Timer):
    '''
    Timer的改进，可循环执行某函数
    '''
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


class LoginPage(tk.Frame):
    '''
    登录的界面
    '''
    def __init__(self, master, connector, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        tk.Label(self, text='请输入用户ID').pack(padx=10, pady=5)
        self.connect = connector
        self.playerid = tk.IntVar()
        self.entry_id = tk.Entry(self, textvariable=self.playerid,
                                validate='key', validatecommand=(isinstance, int))
        self.entry_id.pack(padx=10, pady=5)
        self.button_login = tk.Button(self, text='登录', command=self.login)
        self.button_login.pack(padx=10, pady=5)

    def login(self):
        '''
        按下登录按钮后的行为
        '''
        self.master.toMenuPage()


class MenuPage(tk.Frame):
    '''
    登录后的主界面，有开始游戏按钮
    '''
    def __init__(self, master, connector, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.connect = connector
        self.button_start = tk.Button(self, text='开始游戏', command=self.start_game)
        self.button_start.pack(padx=10, pady=5)
        self.canvas = tk.Canvas(self, width=128, height=128)
        self.icons_load = [tk.PhotoImage(file='res/loading.gif', format=('gif -index %d' % i)) for i in range(12)]
        self._icon_index = 0
        self.icon_timer = LoopTimer(0.1, self._change_icon)
        self.i = 0

    def start_game(self):
        '''
        按下"开始游戏"按钮
        :return:
        '''
        self.canvas.pack(padx=10, pady=5)
        self._change_icon()
        self.icon_timer.start()

    def _change_icon(self):
        # self.after(100, self._change_icon)
        self.canvas.create_image(0, 0, anchor='nw',image=self.icons_load[self._icon_index])
        self._icon_index = (self._icon_index + 1) % 12
        self.i += 1
        if self.i > 100:
            self.icon_timer.cancel()


class MainForm(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title = '吃鸡版坦克大战'

        self.connect = None

        self.login_page = LoginPage(self, self.connect)
        self.menu_page = MenuPage(self, self.connect)
        self.login_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)
        self.menu_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1)

        self.login_page.lift()

    def toMenuPage(self):
        self.menu_page.lift()


if __name__ == '__main__':
    mainform = MainForm()
    mainform.mainloop()
