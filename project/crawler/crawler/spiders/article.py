import scrapy
from scrapy.http import Request
from crawler.crawler.utils import get_global_settings
from db import get_collection_article,find_one
from crawler_assist.tidy_req_data import TidyReqData
from crawler.crawler.items.crawl_article import CrawlArticleItem,CrawlArticleReadDataItem
from time import time
from ui import gc
import datetime


class ArticleSpider(scrapy.Spider):
    """
    公众号文章内容爬虫
    """
    name = 'article'
    allowed_domains = ['mp.weixin.qq.com']
    start_url = []
    custom_settings = get_global_settings()
    wx_num,_,_ = TidyReqData.get_gzh_req_data()
    # 担心ip被封 设置请求间隔
    # custom_settings['DOWNLOAD_DELAY'] = 0.5
    custom_settings['DOWNLOADER_MIDDLEWARES'] = {
        'crawler.crawler.middlewares.crawl_article.CrawlArticleMiddleware': 543,
    }
    custom_settings['ITEM_PIPELINES'] = {
        'crawler.crawler.pipelines.crawl_article.ResponseArticlePipeline': 300,
    }
    custom_settings['DOWNLOAD_TIMEOUT'] = 10
    custom_settings['CONCURRENT_REQUESTS'] = 16

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        实例化爬虫需要调用的函数
        """
        # 包含当前公众号所有不存在文本内容数据的生成器
        self.current_nickname = TidyReqData.get_nickname()
        self.articles_list = get_collection_article(self.current_nickname,article={"$exists": False},title={"$exists": True})
        self.crawler_begin_time = time()
        self.crawler_parse_counter = 0

    def start_requests(self):
        """
        :return:重新爬虫的入口函数, 否者直接请求start_urls中的各个url
        重写之后手动调用Request并指定回调函数例如self.parse
        """
        for article in self.articles_list:
            if "weixin" in article['content_url']:
                yield Request(url=article['content_url'],callback=self.parse)

    def parse(self, response):
        """
        :param response:
        :return:请求完成之后的回调函数
        """
        item = CrawlArticleItem()
        item['article_data'] = response.get_ext_data['article_data']
        item['nickname'] = response.get_ext_data['nickname']
        item['raw_url'] = response.get_ext_data['raw_url']
        self.crawler_parse_counter += 1
        time_gap = time()-self.crawler_begin_time
        print(round(time_gap/self.crawler_parse_counter,3),item['article_data']['article'].replace('\n',''))
        # 发送状态给前端
        crawling_item = {}
        crawling_item['nickname'] = item['nickname']
        crawling_item['percent'] = self.crawler_parse_counter
        crawling_item['more'] = round(time_gap/self.crawler_parse_counter,3)
        crawling_item['title'] = find_one(item['nickname'],item['raw_url'])['title'][:10]
        gc.report_crawling(crawling_item)
        yield item

    def close(self, reason):
        """
        :param reason:
        :return:所有url请求完毕之后关闭爬虫的回调函数
        """
        time_gap = time()-self.crawler_begin_time
        if self.crawler_parse_counter != 0:
            print("%s爬虫关闭 用时%d 共计爬取%d 平均%f"%(self.name, time_gap, self.crawler_parse_counter, time_gap/self.crawler_parse_counter))
        from instance.global_instance import gs
        print("正在为 %s 创建索引..."%(self.current_nickname))
        index_result = gs.index_db_docs(self.current_nickname)
        print("索引完成",index_result)
        from db.meta_data import insert_article_metadata
        insert_article_metadata(self.current_nickname,{'date':datetime.datetime.now(),'articles_num':self.crawler_parse_counter})

class ArticleReadDataSpider(scrapy.Spider):
    """
    公众号文章阅读数据爬虫
    """
    name = 'read_data'
    allowed_domains = ['mp.weixin.qq.com']
    start_url = []
    custom_settings = get_global_settings()
    wx_num,_,_ = TidyReqData.get_gzh_req_data()
    if wx_num == 0:
        wx_num = 1
    custom_settings['DOWNLOAD_DELAY'] = round(2.5/wx_num,2)
    custom_settings['DOWNLOADER_MIDDLEWARES'] = {
        'crawler.crawler.middlewares.crawl_article.ArticleReadDataMiddleware': 543,
    }
    custom_settings['ITEM_PIPELINES'] = {
        'crawler.crawler.pipelines.crawl_article.ResponseArticleReadDataPipeline': 300,
    }
    custom_settings['CONCURRENT_REQUESTS'] = 1

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        实例化爬虫需要调用的函数
        """
        # 包含当前公众号所有不存在文本内容数据的生成器
        self.current_nickname = TidyReqData.get_nickname()
        print(self.current_nickname)
        articles_list = get_collection_article(self.current_nickname,read_num={"$exists": False},comment_id={"$exists": True})
        self.articles_list = []
        for article in articles_list:
            self.articles_list.append(article)
        self.task_num = len(self.articles_list)
        self.task_counter = 0
        self.begin_time = time()
        self.pre_time = time()

    def start_requests(self):
        """
        :return:重新爬虫的入口函数, 否者直接请求start_urls中的各个url
        重写之后手动调用Request并指定回调函数例如self.parse
        """
        for article in self.articles_list:
            if ':' in article['content_url']:
                request = Request(url=article['content_url'],callback=self.parse, dont_filter=False)
                request.set_ext_data({'content_url':article['content_url'],
                                      'comment_id':article['comment_id']})
                yield request

    def parse(self, response):
        """
        :param response:
        :return:请求完成之后的回调函数
        """
        item = CrawlArticleReadDataItem()
        item['read_data'] = response.get_ext_data['read_data']
        item['nickname'] = response.get_ext_data['nickname']
        item['content_url'] = response.get_ext_data['content_url']
        # 打印状爬虫状态信息
        self.task_counter += 1
        pre_time_gap = time()-self.pre_time
        total_time_gap = time()-self.begin_time
        time_need = (self.task_num-self.task_counter)*(total_time_gap/self.task_counter)
        print(round(pre_time_gap,2),
              round(total_time_gap/self.task_counter,2),
              "%d/%d"%(self.task_counter,self.task_num),
              response.get_ext_data['read_data']['read_num'],
              response.get_ext_data['read_data']['like_num'],
              response.get_ext_data['read_data']['nick_name'],
              str(datetime.timedelta(seconds=time_need)).split('.')[0]
              )
        self.pre_time = time()
        crawling_item = {}
        crawling_item['nickname'] = item['nickname']
        crawling_item['percent'] = '%d/%d'%(self.task_counter,self.task_num)
        crawling_item['more'] = response.get_ext_data['read_data']['read_num']
        crawling_item['title'] = find_one(item['nickname'],item['content_url'])['title'][:10]
        gc.report_crawling(crawling_item)
        yield item

    def close(self, reason):
        """
        :param reason:
        :return:所有url请求完毕之后关闭爬虫的回调函数
        """
        print(self.name,"爬虫关闭")
