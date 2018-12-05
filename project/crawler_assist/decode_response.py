"""
当如预期得到服务器返回的数据之后，需要对数据做出清理工作以方便scrapy item pipeline
处理处理数据 对数据做出正确的清理工作均存放于此
"""
from crawler_assist.config import REG_COMMENT_ID,REG_VIDEO_NUM,REG_PIC_NUM
from lxml.etree import tostring
import re
import html2text
import json
from tools.utils import logging
from datetime import datetime
html_to_text = html2text.HTML2Text()
logger = logging.getLogger(__name__)


class DecodeArticle():
    """
    解析文章内容
    """
    @staticmethod
    def decode_content(r):
        """
        :param r:html字符串
        :return:解析文章html
        文章html中包含的信息非常丰富 不仅仅只有文章文本等基本数据还有comment_id
        video_num pic_num 还有原文的markdown信息
        """
        data = {}
        r_data = r
        data['video_num'] = len(re.findall(REG_VIDEO_NUM, r_data))
        data['pic_num'] = len(re.findall(REG_PIC_NUM, r_data))
        data['comment_id'] = re.findall(REG_COMMENT_ID, r_data)
        if len(data['comment_id'])==1:data['comment_id']=data['comment_id'][0].split('"')[1]
        else:data['comment_id'] = str(0)
        r_data = DecodeArticle.part_of_html(r_data)
        try:
            data['article'] = html_to_text.handle(r_data)
        except Exception as e:
            try:
                data['article'] = html_to_text.handle(r)
            except:
                data['article'] = ""
        return data

    @staticmethod
    def part_of_html(raw_html,x_path=r'//div[@id="js_content"]'):
        """
        :param x_path:xpath表达式默认获取微信公众号的正文xpath
        :param raw_html:r.text
        :return: 截取html的一部分
        """
        from lxml import html
        tree = html.fromstring(raw_html)
        data = tree.xpath(x_path)
        if len(data) == 1:
            data = tostring(data[0], encoding='unicode')
            return data
        else:
            return raw_html

class DecodeArticleList():
    """
    解析获取文章列表
    """
    @staticmethod
    def decode_load_more(response):
        """
        :param response:请求返回的response
        :return:提取历史文章列表信息并且分类主副 主文章是一次推送的头条消息用10表示 其余文章从11开始表示
            r['r']['data']: title,digest,content_url,source_url,cover,author,mov,p_date,id
            r['r']['des']: can_msg_continue,next_offset
        """
        use_data = dict()
        use_data['data'] = []
        use_data['des'] = {}
        use_data['id'] = 0

        data = json.loads(response.body_as_unicode())
        # 添加本次获取列表之后是否可以继续以及下一个offset
        use_data['des']['can_msg_continue'] = data['can_msg_continue']
        use_data['des']['next_offset'] = data['next_offset']
        # 遍历消息列表
        data = DecodeArticleList.general_msg_list_to_list(data.get('general_msg_list'))
        # 解析消息列表
        for msg in data:
            p_date = msg.get("comm_msg_info").get("datetime")
            msg_info = msg.get("app_msg_ext_info")  # 非图文消息没有此字段
            if msg_info:
                mov = 10
                msg_info['mov'] = str(mov)
                DecodeArticleList._insert(use_data, msg_info, p_date)
                multi_msg_info = msg_info.get("multi_app_msg_item_list")
                for msg_item in multi_msg_info:
                    mov += 1
                    msg_item['mov'] = str(mov)
                    DecodeArticleList._insert(use_data, msg_item, p_date)
            else:
                logger.warning(u"此消息不是图文推送，data=%s" % json.dumps(msg.get("comm_msg_info")))
        use_data.pop('id')
        return use_data

    @staticmethod
    def general_msg_list_to_list(general_msg_list):
        msg_list = general_msg_list.replace(r"\/", "/")
        data = json.loads(msg_list)
        return data.get("list")

    @staticmethod
    def _insert(use_data, item, p_date):
        '''
        文章列表信息插入use_data
        '''
        use_data['id'] += 1
        keys = ('title', 'author', 'content_url', 'digest', 'cover', 'source_url','mov')
        sub_data = DecodeArticleList.sub_dict(item, keys)
        p_date = datetime.fromtimestamp(p_date)
        sub_data["p_date"] = p_date
        use_data['data'].append(sub_data)
        logger.info('%d %s %s'%(use_data["id"],sub_data["mov"], sub_data["title"]))

    @staticmethod
    def sub_dict(d, keys):
        import html
        return {k: html.unescape(d[k]) for k in d if k in keys}

