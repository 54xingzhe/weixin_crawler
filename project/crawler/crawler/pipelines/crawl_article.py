from db import update_article_from_template
from db import update_one


class ResponseArticlePipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        article_data = item['article_data']
        nickname = item['nickname']
        article = update_article_from_template(article_data)
        article["content_url"] = item['raw_url']
        update_one(nickname, article)

    def close_spider(self, spider):
        pass


class ResponseArticleReadDataPipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        read_data = item['read_data']
        nickname = item['nickname']
        read_data = update_article_from_template(read_data)
        read_data["content_url"] = item['content_url']
        update_one(nickname, read_data)

    def close_spider(self, spider):
        pass
