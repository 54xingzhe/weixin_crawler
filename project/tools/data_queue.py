"""
实现了redis和mongodb的队列API 两者API并非一致 实际上应该对外提供一致的API
"""
from datetime import datetime
from tools.utils import logging
from instance import db_instance
logger = logging.getLogger(__name__)
from instance import redis_instance
from copy import copy


# redis队列
class RQ():
    """
    使用redis创建一个队列FIFO
    """
    def __init__(self, q_name):
        """
        :param q_name:创建一个队列 开头处插入一个__BEGIN
        所有队列名称均以re__开头
        """
        self.q_name = 'rq__'+q_name
        self.redis = redis_instance

    def push(self, data):
        """
        :param data:
        :return:1表示插入成功 1表示对象已经存在
        """
        rq = self.get_rq_data()
        if data not in rq:
            self.redis.lpush(self.q_name,data)
            return 1
        return 0

    def pop(self):
        """
        :return:[]表示队列已经空了
        """
        data = self.redis.rpop(self.q_name)
        try:
            rq_j_data = json.loads(data)
        except:
            if data:
                rq_j_data = data.decode('utf8')
            else:
                rq_j_data = []
        return rq_j_data

    def delete_rq(self):
        self.redis.delete(self.q_name)

    def remove(self,data):
        """
        :param data:根据data删除指定的元素
        :return:删除后的队列
        """
        rq_list = self.get_rq_data()
        self.delete_rq()
        for item in reversed(rq_list):
            if item is not data:
                self.push(item)
        rq_list = self.get_rq_data()
        return rq_list

    def get_rq_data(self):
        """
        :return:返回插入的数据
        """
        rq_b_data_list = self.redis.lrange(self.q_name,0,-1)
        rq_j_data_list = []
        for rq_b_data in rq_b_data_list:
            try:
                rq_j_data = json.loads(rq_b_data)
            except:
                rq_j_data = rq_b_data.decode('utf8')
            rq_j_data_list.append(rq_j_data)
        return rq_j_data_list


    def get_rqs(self):
        rqs = self.redis.keys("rq__*")
        return rqs


"""
数据库队列
"""
data_queue_scheme = {
    "name"          : "",# 队列名称
    "queue_type"    : "",# 备用名
    "update_time"   : 0 ,# 上次更新时间
    "length"        : 0 ,# 队列长度
    "ext_data"      : {},# 附加数据
    "queue"         : [],# 队列数据
}

class DBQ():
    """
    持久型数据库队列维护, 一条记录通常是一个类别, 类别中有一个list用户维护该类别的成员
    类别的主要属性是meta和data 所有DBQ均在同一个collection中 一个DBQ就是一条记录
    一个DBQ实例在数据库中queue为一条记录
    """
    queue_name = 'queue'
    col = db_instance[queue_name]
    def __init__(self, name, queue_type):
        """
        :param name:队列名称
        :param queue_type:队列类型 通常用于标识用途
        """
        self.name = name
        self.queue_type = queue_type
        self.queue_structure = copy(data_queue_scheme)
        # name, queue_type唯一标识一个queue
        self.queue_structure['name'] = name
        self.queue_structure['queue_type'] = queue_type
        # 初始化之后创建一个空的队列
        queue_data = DBQ.col.find_one({'name':self.name, 'queue_type':self.queue_type})
        if type(queue_data) is not dict:
            queue_data = copy(self.queue_structure)
            DBQ.col.insert_one(queue_data)

    def add_element(self, element):
        """
        :param element:元素数据 elemet是一个dict 必须指定id属性
        :return:增加一个元素
        """
        queue_data = DBQ.col.find_one({'name':self.name, 'queue_type':self.queue_type})
        # 更新
        if type(queue_data) is dict:
            self.update_element(element)
        # 插入
        else:
            queue_data = copy(self.queue_structure)
            queue_data['update_time'] = datetime.now()
            queue_data['length'] = 1
            queue_data['queue'] = [element]
            DBQ.col.insert_one(queue_data)
        return queue_data


    def delete_element(self, element):
        """
        :param element:元素数据
        :return: 根据data中的id删除该元素
        1表示产出成功
        0表示未找到匹配id的元素
        """
        queue_data = DBQ.col.find_one({'name':self.name, 'queue_type':self.queue_type})

        elements = queue_data['queue']
        for ele in elements:
            if ele['id'] == element['id']:
                elements.remove(ele)
                queue_data['update_time'] = datetime.now()
                queue_data['length'] -= 1
                DBQ.col.update_one({'name':self.name, 'queue_type':self.queue_type},{"$set":queue_data})
                return 1
        return 0

    def update_element(self, element):
        """
        :param element: 元素数据
        :return:根据data中的id更新该元素
        """
        # 得到队列 如果存在返回dict否则返回None
        queue_data = DBQ.col.find_one({'name':self.name, 'queue_type':self.queue_type})
        old_list = queue_data['queue']
        # 根据elemet更新队列
        result = DBQ.update_dict_list_by_kv(old_list=old_list,element=element)
        queue_data['queue'] = old_list
        queue_data['update_time'] = datetime.now()
        # 如果是新增元素长度自增1
        if result == 2:
            queue_data['length'] += 1
        DBQ.col.update_one({'name':self.name, 'queue_type':self.queue_type},{"$set":queue_data})

    def delete_all_element(self):
        """
        :return:清空队列中的元素
        """
        queue_data = DBQ.col.find_one({'name':self.name, 'queue_type':self.queue_type})
        queue_data['queue'] = []
        DBQ.col.update_one({'name':self.name, 'queue_type':self.queue_type},{"$set":queue_data})

    def delete_self(self):
        """
        :return:删除队列自己
        """
        DBQ.col.delete_one({'name':self.name, 'queue_type':self.queue_type})

    def get_queue(self):
        """
        :return:获得queue list数据
        """
        queue_data = DBQ.col.find_one({'name':self.name, 'queue_type':self.queue_type})
        return queue_data['queue']

    def set_ext_data(self, ext_data):
        """
        :param ext_data:字典
        :return: 设置ext_data
        """
        queue_data = DBQ.col.find_one({'name':self.name, 'queue_type':self.queue_type})
        queue_data['ext_data'] = ext_data
        DBQ.col.update_one({'name':self.name, 'queue_type':self.queue_type},
                           {"$set":queue_data})

    def get_ext_data(self):
        """
        :return: 获取ext_data字典
        """
        queue_data = DBQ.col.find_one({'name':self.name, 'queue_type':self.queue_type})
        if type(queue_data) is dict:
            return queue_data['ext_data']
        return None

    @staticmethod
    def update_dict_list_by_kv(old_list, element, key='id'):
        """
        :param key:
        :param value:
        :return:根据给定字典中的某个键值对跟新所在list, 以保证list中元素的唯一性
        返回0表示失败
        返回1表示更新
        返回2表示增加
        """
        if key not in element:
            logger.warning("key不存在更新list失败%s"%(str(key)))
            return 0
        for ele in old_list:
            if ele[key] == element[key]:
                old_list[old_list.index(ele)] = element
                return 1
        old_list.append(element)
        return 2

    @classmethod
    def get_queue_by_kv(cls, **kwargs):
        """
        :param valye:
        :return:通过特定的键值对组合获取合适的队列
        """
        queue_gen = DBQ.col.find(kwargs)
        queue_list = []
        for queue in queue_gen:
            queue_list.append(queue)
        return queue_list


    @classmethod
    def delete_all_queue(cls):
        """
        :return:删除所有队列
        """
        DBQ.col.delete_many()

    @classmethod
    def delete_queue(cls,name,queue_type):
        """
        :param name: 队列名称
        :param queue_type: 队列类型
        :return: 获取指定名称和类型的队列
        """
        DBQ.col.delete_one({'name':name,'queue_type':queue_type})
