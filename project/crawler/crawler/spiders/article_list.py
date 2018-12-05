import scrapy
from scrapy.http import Request
from crawler.crawler.utils import get_global_settings
from crawler.crawler.items.load_more import LoadMoreItem
from crawler_assist.tidy_req_data import TidyReqData
from ui import gc


class ArticleListSpider(scrapy.Spider):
    name = 'article_list'
    allowed_domains = ['mp.weixin.qq.com']
    start_url = []
    custom_settings = get_global_settings()
    wx_num,_,_ = TidyReqData.get_gzh_req_data()
    if wx_num == 0:
        wx_num = 1
    custom_settings['DOWNLOAD_DELAY'] = round(2.0/wx_num,2)
    custom_settings['ITEM_PIPELINES'] = {
        'crawler.crawler.pipelines.load_more.ResponseArticleListPipeline': 300,
    }
    custom_settings['DOWNLOADER_MIDDLEWARES'] = {
        'crawler.crawler.middlewares.load_more.LoadMoreMiddleware': 543,
    }
    counter = 0
    list_offset = 0

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        实例化爬虫需要调用的函数
        """
        self.current_nickname = ''

    def start_requests(self):
        """
        :return:重新爬虫的入口函数, 否者直接请求start_urls中的各个url
        重写之后手动调用Request并指定回调函数例如self.parse
        """
        yield Request(url='http://www.aii.com',
                      meta={"list_offset":self.list_offset} ,
                      callback=self.parse, dont_filter=True)

    def parse(self, response):
        """
        :param response:
        :return:请求完成之后的回调函数
        """
        self.counter += 1
        cmc = response.get_ext_data['can_msg_continue']
        next_offset = response.get_ext_data['next_offset']
        item = LoadMoreItem()
        item['article_list'] = response.get_ext_data['data']
        item['nickname'] = response.get_ext_data['nickname']
        self.current_nickname = response.get_ext_data['nickname']
        gc.report_crawling({'nickname':item['nickname'],
                            'percent':'UNK',
                            'more':cmc,
                            'title':len(item['article_list'])})
        yield item
        if cmc == 1:
            yield Request(url='http://www.aii.com',
                          meta={"list_offset":next_offset} ,
                          callback=self.parse, dont_filter=True)

    def close(self, reason):
        """
        :param reason:
        :return:所有url请求完毕之后关闭爬虫的回调函数
        """
        # 删除被删除的公众号 被删除的公众号content_url为空
        from db import delete
        delete(self.current_nickname, content_url="")
        print(self.name,"爬虫关闭")
