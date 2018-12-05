from scrapy import signals
from crawler_assist.tidy_req_data import TidyReqData
from crawler_assist.decode_response import DecodeArticleList
from tools.utils import dict_to_str


class LoadMoreMiddleware():
    counter = 0
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        current_req_data = self.req_data_list[self.counter%self.wx_num]
        req_data = TidyReqData.req_to_dict(current_req_data['load_more']['req_data'])
        request.set_method(req_data['method'])
        req_data['url_param_dict']['offset'] = request.meta['list_offset']
        url = req_data['url']+dict_to_str(req_data['url_param_dict'])
        request._set_url(url)
        request.set_headers(req_data['headers'])
        self.counter += 1
        return None

    def process_response(self, request, response, spider):
        use_data = DecodeArticleList.decode_load_more(response)
        response.set_ext_data({'can_msg_continue':use_data['des']['can_msg_continue'],
                               'next_offset':use_data['des']['next_offset'],
                               'data':use_data['data'],
                               'nickname':self.req_data_list[0]['nickname']})
        return response

    def spider_opened(self, spider):
        self.wx_num,self.req_data_dict,self.req_data_list = TidyReqData.get_gzh_req_data()
