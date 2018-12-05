from scrapy import signals
from crawler_assist.tidy_req_data import TidyReqData
from crawler_assist.decode_response import DecodeArticle
from tools.utils import str_to_dict,dict_to_str
import json
from datetime import datetime
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from copy import copy


class CrawlArticleMiddleware():
    counter = 0
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        current_req_data = self.req_data_list[self.counter%self.wx_num]
        req_data = TidyReqData.req_to_dict(current_req_data['content']['req_data'])
        url = request._get_url()
        raw_url = copy(url)
        if "https" in raw_url:
            raw_url = raw_url.replace("https","http")
        request.set_ext_data({"raw_url":raw_url})
        if "https" not in url:
            url = url.replace("http","https")
        request._set_url(url)
        request.set_method(req_data['method'])
        if "Cookie" in req_data['headers']:
            req_data['headers'].pop("Cookie")
        request.set_headers(req_data['headers'])
        self.counter += 1
        return None

    def process_response(self, request, response, spider):
        r_body = response.body_as_unicode()
        if "访问过于频繁，请用微信扫描二维码进行访问" in r_body:
            print("IP被限制 一天之内无法通过局域网查看请更换IP")
            spider.crawler.engine.close_spider(spider, 'IP被限制 一天之内无法通过局域网查看请更换IP')
        article_data = DecodeArticle.decode_content(r_body)
        response.set_ext_data({"article_data":article_data,
                               "nickname":spider.current_nickname,
                               "raw_url":request.get_ext_data["raw_url"]})
        return response

    def spider_opened(self, spider):
        self.wx_num,self.req_data_dict,self.req_data_list = TidyReqData.get_gzh_req_data()
        if self.wx_num == 0:
            self.wx_num = 1


class ArticleReadDataMiddleware():
    counter = 0
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        current_req_data = self.req_data_list[self.counter%self.wx_num]
        req_data = TidyReqData.req_to_dict(current_req_data['getappmsgext']['req_data'])
        content_url = request._get_url()
        content_url_param_dict = str_to_dict(content_url.split('?')[-1],'&','=')
        body_dict = req_data['body_dict']
        body_dict.update(content_url_param_dict)
        body_dict['comment_id'] = request.get_ext_data['comment_id']
        body_dict['is_need_reward'] = 1
        if body_dict['comment_id'] == '0':
            body_dict['scene'] = 38
        else:
            body_dict['scene'] = 27
        url = req_data['url']+req_data['url_param_str']
        request._set_url(url)
        request.set_method(req_data['method'])
        request.set_headers(req_data['headers'])
        body_str = dict_to_str(body_dict)
        request._set_body(body_str)
        self.counter += 1
        return None

    def process_response(self, request, response, spider):
        js = json.loads(response.body_as_unicode())
        read_data = {}
        if "read_num" not in js.get("appmsgstat"):
            print(js)
            spider.crawler.engine.close_spider(spider, '请求参数过期')
        read_data['read_num'] = js.get("appmsgstat").get("read_num")
        read_data['like_num'] = js.get("appmsgstat").get("like_num")
        read_data['reward_num'] = js.get("reward_total_count")
        read_data['nick_name'] = js.get("nick_name")#  已登陆的微信名称
        if read_data['reward_num'] is None:
            read_data['reward_num'] = -1
        read_data['c_date'] = datetime.now()
        read_data['comment_num'] = js.get("comment_count")
        if read_data['comment_num'] is None:
            read_data['comment_num'] = -1
        response.set_ext_data({"read_data":read_data,
                               "nickname":spider.current_nickname,
                               "content_url":request.get_ext_data["content_url"]})
        return response

    def spider_opened(self, spider):
        self.wx_num,self.req_data_dict,self.req_data_list = TidyReqData.get_gzh_req_data()
        if self.wx_num == 0:
            self.wx_num = 1
