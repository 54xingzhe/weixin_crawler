from phone_operate.config import BTN, CROP_RANGE, UI_WORDS
from phone_operate.config import KEY
import time
from random import randint
from phone_operate.PhoneControl import OperateAllPhone
from phone_operate.VC import VC
from instance import redis_instance
from crawler_assist.tidy_req_data import TidyReqData



class WeixinOperate():
    """
    实现对所有在线手机进行操作 以获取微信请求参数
    """
    busy = 0
    def __init__(self, phone_list):
        self.oap = OperateAllPhone(phone_list)
        self.home_weixin = {} #桌面微信位置
        self.main_bottom = {} #微信主界面底部四大按钮位置
        self.gzh_folder = {} #公众号文件夹位置
        # 找一个手机的界面作为眼睛
        self.vc = VC(phone_list[0])

    def home(self):
        """
        :return:通过多次点击BACK按键回到主界面 之所以不直接点击HOME按键 是需要层层返回微信到主界面
        """
        for i in range(7):
            self.oap.key(KEY['BACK_KEYEVENT'])
            time.sleep(0.3)
        return KEY['BACK_KEYEVENT']

    def home_to_gzh_search(self):
        """
        :return:从主界面到公众号搜索
        """
        # 点击微信图标
        self.oap.tap(BTN['EMU_WEIXIN_ICON'])
        time.sleep(0.5)
        # 点击通信录
        self.oap.tap(BTN['TONGXUNLU_BTN'])
        time.sleep(0.5)
        # 点击公众号
        self.oap.tap(BTN['GZH_FOLDER'])
        time.sleep(0.5)
        # 点击搜索
        self.oap.tap(BTN['SEARCH_BTN'])
        time.sleep(1)
        return 0

    def search_gzh(self, nickname):
        """
        :param nickname:待搜索公众号名称
        :return:
        """
        # 输入拼音
        self.oap.text(nickname)
        time.sleep(0.5)
        # 进入账号
        self.oap.tap(BTN['FIRST_GZH_SEARCH_RESULT'])
        time.sleep(0.5)
        #键入主界面
        self.oap.tap(BTN['PROFILE_BTN'])
        time.sleep(0.5)
        # 上拉
        self.oap.roll(0,500)
        time.sleep(0.5)
        return 0

    def all_message(self):
        """
        :return:从公众号主页下拉点击全部消息消息
        """
        # 全部消息
        all_message_pos = self.vc.click_by_words("全部消息",tap=False)
        self.oap.tap(all_message_pos)
        time.sleep(5)
        self.oap.roll(0,500)
        time.sleep(2)
        return 0

    def click_a_message(self, args=2):
        """
        :return:来到历史列表之后随机点击一篇文章
        """
        #获取界面文章标题消息
        if args==1:corp = CROP_RANGE['PROFILE_MESSAGE_LIST']
        elif args==2:corp = CROP_RANGE['MESSAGE_LIST']
        ui_words = self.vc.get_ui_words(location=True, crop=corp)
        #随便点一个标题
        random_index = randint(1,len(ui_words))-1
        loc = ui_words[random_index]['location']
        pos = [loc['left'],loc['top'],loc['left']+loc['width'],loc['top']+loc['height']]
        self.oap.tap(pos)
        #等待页面加载完毕
        time.sleep(5)
        self.oap.roll(0,500)
        time.sleep(1)


    def check_comments(self):
        """
        :return:成功打开一篇文章之后 拉到底检查评论信息
        """
        # 拉到底
        for i in range(2):
            self.oap.roll(0,500)
            time.sleep(1)
        time.sleep(2)
        # 检查有无评论 有评论 无评论 有广告 三种情况
        ui_words_str = self.vc.get_ui_words(location=False,in_str=True,crop=CROP_RANGE['LEAVE_MSG_BOTTOM'])
        # 如果暂无评论点击了留言按钮
        if UI_WORDS['NO_LEAVING_MSG'] in ui_words_str:
            print('点击了留言信息。。。')
            self.oap.tap(BTN['LEAVE_MSG'])
            time.sleep(1)
            self.oap.key(KEY['BACK_KEYEVENT'])

    def get_all_req_data(self, nickname, hand=False):
        """
        获取关于一个公众号的全部请求数据 当前程序使用baidu API受到网络和并发限制效果并十分理想
        :param nickname: 公众号昵称
        :return:最后成功与否取决在redis中是否找到有有效数据
        """
        TidyReqData.flush_data("*.req")
        redis_instance.set('current_nickname',nickname)
        self.home_to_gzh_search()
        self.search_gzh(nickname)
        if hand==False:
            self.all_message()
            self.click_a_message()
            # self.check_comments()
        else:
            input("请一一手动或取参数 回车退出")
        self.home()

    def get_part_req_data(self, nickname):
        """
        仅获取阅读量和评论的请求数据
        :param nickname:公众号昵称
        :return:最后成功与否取决在redis中是否找到有有效数据
        """
        TidyReqData.flush_data()
        redis_instance.set('current_nickname',nickname)
        self.home_to_gzh_search()
        self.search_gzh(nickname)
        self.click_a_message(args=1)
        self.check_comments()
        self.home()
