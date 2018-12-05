# 将图片转化为文字和像素位置信息
from aip import AipOcr
from configs.auth import APP_ID, API_KEY, SECRET_KEY
from phone_operate.config import OCR_NO_WORDS
from PIL import Image
from tools.utils import logging
logger = logging.getLogger(__name__)

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


class OCR():
    @staticmethod
    def get_file_content(filePath):
        """
        :param filePath: 文件地址
        :return: 读取的图片文件
        """
        with open(filePath, 'rb') as fp:
            return fp.read()

    @staticmethod
    def pre_process_img(pic_file_name, quality=50, crop=None):
        """
        :param pic_file_name:待压缩图片名称
        :param quality:质量百分数
        :param crop:(left, top, right, bottom)裁剪左上角和右下角的绝对坐标
        :return: 压缩图片并且返回压缩只有图片的名称
        """
        im = Image.open(pic_file_name)
        rgb_im = im.convert('RGB')
        if crop:
            rgb_im = rgb_im.crop(crop)
        rgb_im.save(pic_file_name+'.jpg', optimize=True, quality=quality)
        return pic_file_name+'.jpg'

    @staticmethod
    def ocr(pic_file_name, location=False, quality=50, crop=None):
        """
        根据包含路径的图片文件名调用API返回cor结果
        :param pic_file_name:根据包含路径的图片文件名
        :param location:是否需要识别位置信息 需要位置信息 True 表示需要
        :return:
        有位置信息
        [{'location': {'height': 59,'left': 38,'top': 827,'width': 432},
          'words': '网陈苏苏:[链接]'},
         {'location': {'height': 56,'left': 212,'top': 955,'width': 206},
          'words': '服务通知'},...]
        无位置信息
        [{'words': '微信'},
         {'words': '通讯录'},
         {'words': '发现'},
         {'words': '我'}],...
        ]
        """
        compressed_image = OCR.pre_process_img(pic_file_name,quality=quality,crop=crop)
        image = OCR.get_file_content(compressed_image)
        # 带有位置信息
        if location:
            try:
                result = client.general(image)
            except Exception as e:
                logging.error("请求 带位置信息 OCR失败 请检查网络或API可用次数")
                exit()
            # 计算words裁剪之前的真是坐标
            if crop:
                for words in result['words_result']:
                    words['location']['left'] += crop[0]
                    words['location']['top'] += crop[1]
        # 不带位置信息
        else:
            try:
                result = client.basicGeneral(image)
            except Exception as e:
                logging.error("请求 非位置信息 OCR失败 请检查网络或API可用次数")
                exit()
        if result['words_result_num'] != 0:
            return result['words_result']
        else:
            return OCR_NO_WORDS

