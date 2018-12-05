from instance import db_instance
from copy import copy
col = db_instance['crawler_metadata']
"""
用于记录一个公众号的更新历史，更新日期、历史文章列表的加载次数（一次一般是10天的发文列表），文章总数
"""
meta_data_scheme = {
    "nickname"          : "",# 公众号昵称
    "update_log_list"    : "",# date,deepth,article_num
}


def insert_article_metadata(nickname, update_log):
    """
    :param nickname: 更新的公众号昵称
    :param update_log: 更新详细日志
    :return: 一个公众号占用一行记录
    """
    metadata = col.find_one({'nickname':nickname})
    if type(metadata) is dict:
        metadata['update_log_list'].append(update_log)
        col.update_one({'nickname':nickname},{"$set":metadata})
    # metadata不存在
    else:
        metadata = copy(meta_data_scheme)
        metadata['nickname'] = nickname
        metadata['update_log_list'] = [update_log]
        col.insert_one(metadata)


def get_article_metadata(nickname=None, all=True):
    """
    :param nickname:指定账号的日志 None为全部账号
    :param all:True全部日志 False:最后一次更新日志
    :return: 获取公众号文章平爬取的日志信息
    """
    data = {}
    metadata = []
    if nickname is not None:
        metadata = [col.find_one({'nickname':nickname})]
    else:
        for md in col.find():
            metadata.append(md)
    for item in metadata:
        if all:data[item['nickname']] = item['update_log_list']
        else :data[item['nickname']] = item['update_log_list'][-1]
    return data


def delete_article_metadata(nickname):
    """
    :param nickname: 公众号昵称
    :return: 删除指定公众号的微信爬取日志信息
    """
    col.delete_one({'nickname':nickname})


def update_history():
    """
    :return:为此前通过手动爬取的文章创建metadata
    """
    from db import WeixinDB
    from datetime import datetime
    wxdb = WeixinDB()
    nicknames = wxdb.get_all_nickname(is_count=True)
    for item in nicknames:
        if item[0] not in ['queue','crawler_metadata']:
            insert_article_metadata(item[0],{'date':datetime.now(),'articles_num':item[1]})


if __name__ == "__main__":
    update_history()
