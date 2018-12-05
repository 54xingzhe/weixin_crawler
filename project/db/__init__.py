from instance import db_instance


"""
定义一篇公众号文章在mongodb中的字段
"""
article_scheme = {
    "nickname"          : "" ,#公众号昵称 string
    "title"             : "" ,#文章标题 string
    "article_id"        : 0  ,#一个公众号的文章id int
    "content_url"       : "" ,#文章真实url url
    "source_url"        : "" ,#文章原文url url
    "digest"            : "" ,#人工摘要 string
    "machine_digest"    : "" ,#自动摘要 string
    "cover"             : "" ,#封面url url
    "p_date"            : 0  ,#发布时间 datetime
    "with_ad"           : False ,#有无广告 bool
    "pic_num"           : 0 ,#插图数 int
    "video_num"         : 0 ,#视频数量 int
    "read_num"          : 0 ,#阅读量 int
    "like_num"          : 0 ,#点赞量 int
    "comment_id"        : "" ,#评论id string
    "comment_num"       : 0 ,#评论数量 int
    "comments"          : {} ,#精选评论内容 dict
    "reward_num"        : 0 ,#赞赏数量 int
    "author"            : "" ,#作者 string
    "mov"               : 0 ,#主副 int
    "title_emotion"     : 0 ,#标题情感 int
    "title_token"       : [] ,#标题分词 list
    "title_token_len"   : 0 ,#分词长度 int
    "human_digest_token": [] ,#人工摘要分词 list
    "article"           : "" ,#文本内容 markdown
    "article_token"     : [] ,#正文分词 list
    "article_token_len" : 0 ,#正文分词长度 int
    "c_date"            : 0 ,#爬取时间
}

def update_article_from_template(article_seg):
    """
    :param article_seg: 含有一条article部分或者全部的数据
    :return:根据article_scheme中指定的字段提取article_seg中的数据
    """
    article = {}
    for key in article_scheme:
        if key in article_seg:
            article[key] = article_seg[key]
    return article


def insert_one(nickname, article):
    """
    :param nickname:
    :param article: dict data
    :return: 在nickname collection中插入一公众号文章数据
    """
    col = db_instance[nickname]
    return col.insert_one(article).inserted_id

def update_one(nickname, articel):
    """
    :param nickname:
    :param articel:
    :return: 根据article中的content_url更新文章数据
    """
    op_result = ''
    # 已经删除的文章不存在content_url属性 直接返回局
    if articel["content_url"] is "":
        op_result = 'ERROR'
        return op_result
    col = db_instance[nickname]
    result = col.find_one({"content_url":articel['content_url']})
    if type(result) is dict:
        # 数据存在可以更新
        col.update_one({"content_url":articel['content_url']},
                       {"$set":articel})
        op_result = 'UPDATE'
    else:
        # 数据不存在调用插入
        insert_one(nickname, articel)
        op_result = 'INSERT'
    return op_result


def insert_many(nickname, articles, check_exist=True):
    """
    :param nickname:
    :param articles:article lsit
    :param check_exist:如否需要根据content_url判重
    :return: 在nickname collection中插入一个list的文章
    """
    # 是否存在被更新的记录
    has_update = False
    if check_exist==False:
        col = db_instance[nickname]
        col.insert_many(articles)
    else:
        for article in articles:
            result = update_one(nickname, article)
            if result == 'UPDATE':
                has_update = True
    return has_update


def count(nickname):
    """
    :param nickname:
    :return: 计算当前公众号的文章数量
    """
    return db_instance[nickname].count()


def delete(nickname, **kwargs):
    """
    :param nickname:
    :param kwargs: 用字典表示的过滤器
    :return: 根据match中提供的符合信息删除文章 支持全部删除
    """
    col = db_instance[nickname]
    col.delete_many(kwargs)


def find_one(nickname,content_url):
    """
    :param nickname:
    :param content_url:
    :return:
    """
    col = db_instance[nickname]
    result = col.find_one({'content_url':content_url})
    return result


def drop_collection(nickname):
    """
    :param nickname:
    :return: 删除collection
    """
    db_instance.drop_collection(nickname)
    return nickname


def get_collection_article(nickname,**kwargs):
    """
    :param nickname: 
    :param kwargs: 例如找出不存在article字段的所有数据 {"article":{"$exists": False}}
    :return: 以生成器的形式返回一个公众号的全部或者部分数据
    """
    col = db_instance[nickname]
    articles = col.find(kwargs)
    for article in articles:
        yield article

class WeixinDB():
    """
    针对微信全部数据提供方法 暴露给全部程序可见
    """
    def __init__(self):
        pass

    @staticmethod
    def get_all_nickname(is_count=False):
        """
        :param is_count:是否需要计算collection中的数据数量
        :return: 一个公众号是一个collection 返回全部的collection名称
        """
        nicknames = db_instance.collection_names()
        if is_count is False:
            return nicknames
        else:
            nicknames_count = []
            for nickname in nicknames:
                nicknames_count.append((nickname,count(nickname)))
        return nicknames_count
