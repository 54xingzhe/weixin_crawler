from db import update_article_from_template
from db import insert_many


class ResponseArticleListPipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        article_list = item['article_list']
        nickname = item['nickname']
        tidy_article_list = []
        for article in article_list:
            tidy_article_list.append(update_article_from_template(article))
        print(nickname,tidy_article_list)
        has_update = insert_many(nickname, tidy_article_list)
        if has_update == True:
            print("文章列表已经最新")
            spider.crawler.engine.close_spider(spider, '文章列表已经最新')

    def close_spider(self, spider):
        pass
