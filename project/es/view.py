def search_result_pretty(result):
    """
    :param result:
    :return:格式化es搜索出来的结果，方便ui展示
    """
    # from tools.utils import debug_p
    # debug_p(result)
    r = {}
    r['total'] = result['total']
    r['data'] = []
    for article in result['hits']:
        article['_source']['highlight'] = ''.join(article['highlight']['article']).replace('\n','')
        r['data'].append(article['_source'])
    return r
