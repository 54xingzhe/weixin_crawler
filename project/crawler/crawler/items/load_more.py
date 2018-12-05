import scrapy


class LoadMoreItem(scrapy.Item):
    article_list = scrapy.Field()
    nickname = scrapy.Field()
