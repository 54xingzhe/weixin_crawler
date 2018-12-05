# 中英文混合字符串抽取出汉字拼音首字母并保留所有的非汉字
def to_pinyin(ch_name):
    """
    将混合转化为搜索拼音字符
    INPUT '杭州frank1湖滨银泰in77'
    OUTPUT 'hzfrank1hbytin77'
    """
    from pypinyin import lazy_pinyin
    import re
    d1 = re.sub(r'[a-zA-Z0-9]+',' ',ch_name)
    d2 = re.findall(r'[a-zA-Z0-9]+',ch_name)
    d3 = lazy_pinyin(d1)
    d4 = []
    i=0
    for d in d3:
        if d == ' ':
            d4.append(d2[i])
            i+=1
        else:
            d4.append(d[0])
    d4 = ''.join(d4)
    return d4

def to_pinyin_full(ch_name):
    from pypinyin import lazy_pinyin
    return '_'.join(lazy_pinyin(ch_name), )

# 字符串到字典 支持自定义键值间隔符和成员间隔符
def str_to_dict(s, join_symbol="\n", split_symbol=":"):
    """
    key与value通过split_symbol连接， key,value 对之间使用join_symbol连接
    例如： a=b&c=d   join_symbol是&, split_symbol是=
    :param s: 原字符串
    :param join_symbol: 连接符
    :param split_symbol: 分隔符
    :return: 字典
    """
    s_list = s.split(join_symbol)
    data = dict()
    for item in s_list:
        item = item.strip()
        if item:
            k, v = item.split(split_symbol, 1)
            data[k] = v.strip()
    return data

# 字典转换为字符串
def dict_to_str(data, join_symbol="&", split_symbol="="):
    s = ''
    for k in data:
        s += str(k)+split_symbol+str(data[k])+join_symbol
    return s[:-2]

# 字符串转化为字典
def dictstr_to_dict(str_data):
    import ast
    return ast.literal_eval(str_data)

# 配置日志打印格式
import logging
from configs import LOGGING_LEVEL
logging_level = {
    'CRITICAL':logging.CRITICAL,
    'FATAL':logging.FATAL,
    'ERROR':logging.ERROR,
    'WARNING':logging.WARNING,
    'WARN':logging.WARN,
    'INFO':logging.INFO,
    'DEBUG':logging.DEBUG,
    'NOTSET':logging.NOTSET,
}
logging.basicConfig(
    format = '%(asctime)s %(levelname)-4s %(message)s',
    level=logging_level[LOGGING_LEVEL],
    datefmt='%d %H:%M:%S')

#对齐打印且能通过depth控制打印深度
import pprint
pp = pprint.PrettyPrinter(depth=3)
debug_p = pp.pprint


def sub_list(whole_list, part_list):
    """
    :param whole_list:
    :param part_list:
    :return:从whole list中找出除了part_list之外的元素 组成一个子list返回
    """
    return [x for x in whole_list if x not in part_list]
