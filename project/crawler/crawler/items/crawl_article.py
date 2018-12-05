import scrapy


class CrawlArticleItem(scrapy.Item):
    article_data = scrapy.Field()
    nickname = scrapy.Field()
    raw_url = scrapy.Field()


class CrawlArticleReadDataItem(scrapy.Item):
    read_data = scrapy.Field()
    nickname = scrapy.Field()
    content_url = scrapy.Field()
