from os import system
import random
from threading import Thread


def connect_phone(func):
    """
    装饰器负责每次命令前连接手机
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        system('adb connect '+args[0].phone)
        return func(*args, **kwargs)
    return wrapper


class PhoneControl():
    def __init__(self, phone):
        """
        :param phone:adb 操作手机所需要的端口信息
        """
        self.phone = phone

    def get_phone(self):
        """
        获取实例手机端口信息
        """
        return self.phone

    @connect_phone
    def get_screen_cap(self, file_name='screen_cap'):
        """
        获取截图
        """
        system('adb -s '+str(self.phone)+' shell screencap -p /sdcard/'+file_name+'.png')
        system('adb -s '+str(self.phone)+' pull /sdcard/'+file_name+'.png'+' ./'+file_name+'.png')
        return file_name+'.png'

    @connect_phone
    def input_tap(self, pos):
        """
        点击屏幕
        pos为一个区域的左上与右下坐标
        如果事先已经随机化了pos可以只是一个点 随机点击一个位置是为防止被被认为是机器人
        返回实际点击位置
        """
        if len(pos) == 2:_pos = pos
        else : _pos = (random.randint(pos[0],pos[2]),random.randint(pos[1],pos[3]))
        command = r'adb -s '+str(self.phone)+' shell input tap {} {}'.format(_pos[0],_pos[1])
        system(command)
        return _pos

    @connect_phone
    def input_swipe(self, x1, x2):
        """
        从一个位置滑动到另一位置
        :param x1:起始坐标，屏幕左上角为原点
        :param x2:终点坐标，屏幕左上角为原点
        :return:[x1,x2]
        """
        command = r'adb -s '+str(self.phone)+' shell input swipe {} {} {} {}'.format(x1[0],x1[1],x2[0],x2[1])
        system(command)
        return [x1,x2]

    @connect_phone
    def input_roll(self, dx=0, dy=500):
        """
        拉动屏幕
        :param dx:x方向速度
        :param dy:y方向速度
        :return:[dx, dy]
        """
        command = r'adb -s '+str(self.phone)+' shell input roll {} {}'.format(dx,dy)
        system(command)
        return [dx,dy]

    @connect_phone
    def input_key_event(self, event_cmd):
        """
        按键事件 比如home menue back volum_up volum_down等等 具体定义在配置文件中
        :param event_cmd:事件ID
        :return:event_cmd
        """
        command = r'adb -s '+str(self.phone)+' shell input keyevent '+event_cmd
        system(command)
        return event_cmd

    @connect_phone
    def input_text(self, text):
        """
        输入文本信息 可能不支持中文输入
        :param text:待输入的文本信息
        :return:文本信息
        """
        command = r'adb -s '+str(self.phone)+' shell input text {}'.format(text)
        system(command)
        return text

    @connect_phone
    def input_chn(self, text):
        """
        支持中文 需要事先将ADB键盘设置为默认输入法而且打开软键盘
        :param text:待输入的文本信息
        :return:文本信息
        """
        # adb -s 127.0.0.1:62001 shell am broadcast -a ADB_INPUT_TEXT --es msg "威武之师"
        # command = r'adb -s '+str(self.phone)+' shell am broadcast -a ADB_INPUT_TEXT --es msg {}'.format(text)
        command = r'adb -s '+str(self.phone)+' shell am broadcast -a ADB_INPUT_TEXT --es msg {}'.format(text)
        system(command)
        return text


class OperateAllPhone():
    """
    同时控制给定abd端口的所有手机 请确保手机初始界面一致
    """
    def __init__(self, phone_list):
        """
        :param phone_list:
        """
        self.phone_list = phone_list
        self.pcs = []
        for ap in self.phone_list:
            self.pcs.append(PhoneControl(ap))


    def key(self, event):
        self.operate_all("input_key_event", (event,))

    def text(self, str_data):
        self.operate_all("input_chn", (str_data,))

    def swap(self, x1, x2):
        self.operate_all("input_swipe", (x1,x2))

    def roll(self, dx, dy):
        self.operate_all("input_roll", (dx,dy))

    def tap(self, pos):
        self.operate_all("input_tap", (pos,))

    def print_menue(self):
        menu = {
            "1":"key 按键(3返回4桌面)",
            "2":"text 输入文字",
            # "3":"swap 扫屏",
            # "4":"roll 滚屏",
            # "5":"tap 触摸",
            "6":"quit 退出",
        }
        while True:
            for i in menu:
                print(i, menu[i])
            cmd = input("输入数字指令：")
            print(cmd,'-'*10)
            cmd = cmd.split(' ')
            operation = menu[cmd[0]].split(' ')[0]
            if operation == "quit":
                return
            args = cmd[1]
            print(operation, args)
            self.__getattribute__(operation)(args)


    def operate_all(self, operation, args):
        """
        :param operation: PhoneControl实例方法字符串名称
        :param args:tuple格式参数
        :return:
        """
        _tasks = []
        for pc in self.pcs:
            _tasks.append(Thread(target=pc.__getattribute__(operation), args=args))
        for t in _tasks:
            t.start()
        for t in _tasks:
            t.join()
        return operation
