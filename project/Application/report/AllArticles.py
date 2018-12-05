from db import get_collection_article


def get_all_articles_data(nickname):
    """
    :param nickname:公众号昵称
    :return:一个公众号的全部文章列表
    {'title':'公众号名称','articles':[{},{},{}]}
    """
    use_keys = ['article_id',
                'p_date',
                'read_num',
                'like_num',
                'reward_num',
                'comment_num',
                'author',
                'mov',
                'title',
                'content_url']
    data = {}
    data['title'] = nickname
    data['articles'] = []
    articles = get_collection_article(nickname)
    id_counter = 0
    for article in articles:
        if 'title' not in article:
            continue
        id_counter += 1
        use_data = {}
        # use_data = dict((k, article[k]) for k in use_keys)
        for k in use_keys:
            if k in article:
                use_data[k] = article[k]
            else:
                use_data[k] = '-'
        # 发文时间格式转化
        use_data['p_date'] = use_data['p_date'].strftime("%Y/%m/%d")
        use_data['article_id'] = id_counter
        data['articles'].append(use_data)
    return data
