from phone_operate.OCR import OCR
from phone_operate.PhoneControl import PhoneControl
import numpy as np


class VC(PhoneControl, OCR):
    """
    根据给定的文字或位置信息执行屏幕点击动作 click_by_loc和click_by_words是最重要的连个对外接口
    """
    def __init__(self, phone):
        """
        :param phone:adb 操作手机所需要的端口信息
        """
        # 一下写法不理解参考https://stackoverflow.com/questions/11179008/python-inheritance-typeerror-object-init-takes-no-parameters
        PhoneControl.__init__(self,phone=phone)

    def click_by_words(self,words,tap=True):
        """
        点击指定words所在的区域
        :param words:目标文字
        :return:实际点击的位置
        """
        # 截图
        pic_name = self.get_screen_cap()
        # COR识别ui_words
        ui_words = VC.ocr(pic_name ,location=True)
        # 根据words找最相似
        prob, loc_words = VC.find_position(ui_words, words)
        # 执行点击
        loc = loc_words['location']
        pos = [loc['left'],loc['top'],loc['left']+loc['width'],loc['top']+loc['height']]
        if tap is True:
            self.input_tap(pos)
        return pos

    def click_by_loc(self,pos):
        """
        根据区域位置点击屏幕 同时支持 点位置
        :param pos:区域左上角和右下角的坐标
        :return:
        """
        acture_pos = self.input_tap(pos)
        return acture_pos

    def get_ui_words(self,location=False,in_str=False,crop=None):
        # 截图
        pic_name = self.get_screen_cap()
        # COR识别ui_words
        ui_words = VC.ocr(pic_name ,location=location, crop=crop)
        # 如果不需要位置信息同时需要用一个字符串返回所有的ui界面字符
        if location==False and in_str==True:
            ui_words_str = ''
            for words in ui_words:
                ui_words_str += words['words']
            ui_words = ui_words_str
        return ui_words

    def x_ray(self, keys, crop=None):
        """
        根据给定的关键字返回它们的位置列表 并且给出相似度 大于0.9基本可信
        :param keys:('key1','key2',...)
        :param crop:聚焦裁剪区域 该tuple中信息为(left, upper, right, lower) 左上角为原点
        :return:{'key1':{'pos':[x1,y1,x2,y2],'prob':0.998},'key1':{'pos':[x1,y1,x2,y2],'prob':0.998},...}
        """
        x_ray_data = {}
        # 截图
        pic_name = self.get_screen_cap()
        # 获取图片的ui_words
        ui_words = VC.ocr(pic_name ,location=True, crop=crop)
        for key in keys:
            x_ray_data[key] = {}
            # 找到最相似words
            prob, loc_words = VC.find_position(ui_words, key)
            loc = loc_words['location']
            # 长宽转化为右下角坐标
            pos = [loc['left'],loc['top'],loc['left']+loc['width'],loc['top']+loc['height']]
            x_ray_data[key]['pos'] = pos
            x_ray_data[key]['prob'] = prob
        return x_ray_data

    @staticmethod
    def ui_words2vocb(ui_words):
        """
        根据截屏文字信息获得词典用于接下来创建one_hot向量
        :param ui_words:来自ocr结果
        :return:字典 暂时为未添加停用词
        """
        vocab = ''
        for words in ui_words:
            vocab+=words['words']
        vocab = set(vocab)
        return vocab

    @staticmethod
    def find_position(ui_words, dest_words):
        """
        根据cor识别的ui_words，找到与指定目标dest_words最相似的位置
        :param ui_words:
        :param dest_words:
        :return:第一个返回值为相似度，第二个返回值为对应的ocr信息，包含文本和位置信息
        0.998, {'location': {'width': 119, 'top': 1863, 'left': 345, 'height': 40}, 'words': '通讯录'}
        """
        vocab = VC.ui_words2vocb(ui_words)
        dictionary = list(vocab)
        vec_len = len(dictionary)
        keys = range(vec_len)
        dictionary = dict(zip(dictionary, keys))
        # 计算当ui界面每一行words的one-hot向量
        ui_words_vec = []
        for words in ui_words:
            words_vec = np.zeros(vec_len)
            for word in words['words']:
                words_vec[dictionary[word]]+=1
            ui_words_vec.append(words_vec)
        ui_words_vec = np.array(ui_words_vec)

        # 根据词典计算机目标words的one-hot词向量
        dest_words_vec = np.zeros(vec_len)
        for word in dest_words:
            if word not in dictionary:continue
            dest_words_vec[dictionary[word]]+=1

        #计算余弦夹角
        cos_sim = []
        for vec in ui_words_vec:
            cs = VC.cos_sim(dest_words_vec,vec)
            cos_sim.append(cs)

        #寻找最可能点击位置
        max_index = cos_sim.index(max(cos_sim))
        return cos_sim[max_index], ui_words[max_index]

    @staticmethod
    def cos_sim(a,b):
        """
        计算两个向量的余弦相似性，结果越接近1越相似
        :param a:
        :param b:
        :return:
        """
        cs = np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))
        return cs
