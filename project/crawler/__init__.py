from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from crawler.crawler.spiders.article_list import ArticleListSpider
from crawler.crawler.spiders.article import ArticleSpider,ArticleReadDataSpider


runner = CrawlerRunner()


@defer.inlineCallbacks
def gzh_crawler(config=2):
    """
    :param config:
    1 只获取历史文章列表
    2 获取文章内容并转化为markdown格式
    3 在2的基础上获取文章的阅读量、点赞量、评论量等信息
    :return: 数据存入mongodb 无返回值
    """
    deepth= config
    yield runner.crawl(ArticleListSpider)
    deepth -= 1
    if deepth>0:
        yield runner.crawl(ArticleSpider)
    deepth -= 1
    if deepth>0:
        yield runner.crawl(ArticleReadDataSpider)
    reactor.stop()


def run_crawl(config=2):
    """
    :param config:同gzh_crawler 默认获取文章的文本数据
    :return:
    """
    gzh_crawler(config)
    reactor.run()
    print('所有爬虫结束工作')
    # 由于twisted reactor无法重新启动 一个公众号的爬取任务结束之后重启脚本
    from tools import restart
    restart()

def _run_crawl(config=2):
    """
    :param config:同gzh_crawler 默认获取文章的文本数据
    :return:
    """
    from multiprocessing import Process
    p = Process(target=_run_crawl,args=(config,))
    p.start()
    p.join()
