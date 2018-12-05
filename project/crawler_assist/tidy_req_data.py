from instance import redis_instance
import collections
import json
import re
from tools.utils import str_to_dict


class TidyReqData():
    """
    anyproxy直接将截取的请求数据存放在redis中TidyReqData提供方法整理出每个手机的最新请求文件
    并且删除历史请求文件
    """
    @staticmethod
    def get_all_req_data():
        """
        获取redis中所有的请求文件，也就是key中含有.req字段的记录。最终返回的数据根据key中的时间戳进行排序过
        :return:
        ｛'1532859863455.getappmsgext.req':dict_file,)
          '1523423421446.appmsg_comment.req':dict_file｝
        """
        unordered_req_dict = {}
        ordered_req_dict = collections.OrderedDict()
        # 遍历所有的请求文件
        for key in redis_instance.keys("*.req"):
            req_bin_data = redis_instance.get(key)
            try:
                req_dict_data = json.loads(req_bin_data)
            except:
                req_dict_data = str(req_bin_data)
                # req_dict_data = req_bin_data.decode('utf8')
            unordered_req_dict[key.decode('utf8')] = req_dict_data
        # 按照时间顺序排序之后返回字典
        for key in sorted(unordered_req_dict.keys()):
            ordered_req_dict[key] = unordered_req_dict[key]
        return ordered_req_dict

    @staticmethod
    def add_nick_name(ordered_req_dict):
        """
        :param ordered_req_dict:
        :return:添加nick_name
        """
        wxuin_nn_dict = {}
        nickname = TidyReqData.get_nickname()
        for key in redis_instance.keys("*.nick_name"):
            wxuin_nn_dict[(redis_instance.get(key)).decode('utf8')] = (key.decode('utf8')).split('.')[0]
        for key in ordered_req_dict:
            ordered_req_dict[key]['nick_name'] = wxuin_nn_dict[key]
            ordered_req_dict[key]['wxuin'] = key
            ordered_req_dict[key]['nickname'] = nickname
        return ordered_req_dict

    @staticmethod
    def get_nickname():
        return redis_instance.get('current_nickname').decode('utf8')

    @staticmethod
    def combine(req_dic):
        """
        :param req_dic:
        :return: 找出一个手机(账号)产生的最新请求信息
        ｛
        'wxuin1':{
            'load_more':{'update_time':'1532859858625','req_data':{...}},
            'content':{'update_time':'1532859858625','req_data':{...}},
            'getappmsgext':{'update_time':'1532859858625','req_data':{...}},
            'appmsg_comment':{'update_time':'1532859858625','req_data':{...}}},
        'wxuin2':{
            'load_more':{'update_time':'1532859858625','req_data':{...}},
            'content':{'update_time':'1532859858625','req_data':{...}},
            'getappmsgext':{'update_time':'1532859858625','req_data':{...}},
            'appmsg_comment':{'update_time':'1532859858625','req_data':{...}}},
        }
        """
        tidy_req_dic = {}
        # 建立手机型号索引
        for key in req_dic:
            wxuin = TidyReqData.get_wxuin(req_dic[key])
            if wxuin=="NOT_WEIXIN":
                continue
            tidy_req_dic[wxuin] = {}

        # 为每个wxuin下的数据预留数据类型
        for wxuin in tidy_req_dic:
            tidy_req_dic[wxuin] = {}
        # 组织all_req_data数据
        for key in req_dic:
            key_info = key.split('.')
            # 获取一次请求数据中的元信息
            timestamp = int(key_info[0])
            _type = key_info[1]
            wxuin = TidyReqData.get_wxuin(req_dic[key])
            if wxuin=="NOT_WEIXIN":
                continue
            req_data = req_dic[key]

            # 构造一部手机的模拟请求数据结构
            # 重点关注的是all_req_data部分
            all_req_data = tidy_req_dic[wxuin]
            # 该种类型的请求数据尚未出现
            if _type not in all_req_data:
                all_req_data[_type] = {}
                all_req_data[_type]['update_time'] = timestamp
                all_req_data[_type]['req_data'] = req_data
            # 该种类型的请求数据已经存在根据timetamp和update_time的对比确定是否需要覆盖
            else:
                if timestamp > all_req_data[_type]['update_time']:
                    all_req_data[_type]['update_time'] = timestamp
                    all_req_data[_type]['req_data'] = req_data
        return tidy_req_dic

    @staticmethod
    def tidy():
        """
        对redis中的请求数据整理归纳，找出每台手机最新的请求数据
        :param redis:redis实例 db必须和proxy server存放的db相同
        :return:数据格式见combine 一方面返回字典另一方方面存入redis 并且增加属性 'update_time'
        """
        tidy_req_data = TidyReqData.get_all_req_data()
        tidy_req_data = TidyReqData.combine(tidy_req_data)
        tidy_req_data = TidyReqData.add_nick_name(tidy_req_data)
        redis_instance.set('tidy_req_data',tidy_req_data)
        return tidy_req_data

    @staticmethod
    def get_wxuin(req):
        """
        :param req:
        :return:从redis中一个一条req记录中提取wxuin 用于识别不同的微信账号
        """
        try:
            cookie_string = req["requestOptions"]["headers"]["Cookie"]
        except:
            return "NOT_WEIXIN"
        try:
            wxuin = re.findall(r'wxuin=\S*?;', cookie_string)[0][6:-1]
        except:
            wxuin = cookie_string.split('wxuin=')[-1]
        return wxuin

    @staticmethod
    def flush_data(names=None):
        """
        :param names:可使用通配符格式的key表达式比如 *.req
        :return: 删除redis中的热情数据
        """
        if names==None:
            for key in redis_instance.keys():
                redis_instance.delete(key)
        for key in redis_instance.keys(names):
            redis_instance.delete(key)

    @staticmethod
    def req_to_dict(raw_req_data):
        """
        :param raw_req_data:_type['req_data'] 它只是5种请求数据的一种
        :return:将anyproxy获取的req文件内容解析成为request参数所需要的字典
        """
        req_data = {}
        url_lsit = raw_req_data['url'].split('?')
        url = url_lsit[0]+'?'
        req_data['url'] = url
        req_data['method'] = raw_req_data['requestOptions']['method']
        req_data['headers'] = raw_req_data['requestOptions']['headers']
        body_str = raw_req_data['requestData']
        body_dict = str_to_dict(body_str, "&", "=")
        url_param_str = url_lsit[1]
        url_param_dict = str_to_dict(url_param_str, "&", "=")
        req_data['body_dict'] = body_dict
        req_data['url_param_dict'] = url_param_dict
        # 添加一个测试字段
        req_data['url_param_str'] = url_param_str
        return req_data

    @staticmethod
    def get_gzh_req_data():
        """
        :return:返回为一个公众号准备的所有请求数据
        """
        # 所有请求参数字典格式 使用wxuin作为key
        req_data_dict = TidyReqData.tidy()
        # 所有请求参数list格式 方便按照顺序依次使用各个微信的请求参数
        req_data_list = []
        for key in req_data_dict:
                req_data_list.append(req_data_dict[key])
        # 可用请求参数微信数量
        wx_num = len(req_data_list)
        return wx_num, req_data_dict, req_data_list
