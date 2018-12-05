from tools.data_queue import DBQ
from db.meta_data import get_article_metadata
from tools.utils import sub_list


class GZHSearchSetting():
    """
    公众号搜索设置服务
    和前端设置面板进行交互, 为执行搜索时提供设置参数
    """
    def __init__(self, queue_type='公众号搜索范围设置'):
        self.queue_type = queue_type
        DBQ('公众号',self.queue_type)
        DBQ('类别',self.queue_type)

    def get_all_settings(self):
        """
        :return:返回所有的设置参数字典形式, 以属性之一:搜索范围为例
        当前选用的范围类型, 每种范围类型下已经纳入的元素和尚可纳入的元素
        setting_data = {
            'search_range':{
                'current_search_range':'公众号 or 类别',
                'gzh_members':['爱迪斯','爱迪斯','爱迪斯','爱迪斯'],
                'gzh_available':['爱迪斯','爱迪斯','爱迪斯','爱迪斯'],
                'cat_members':['爱迪斯','爱迪斯','爱迪斯','爱迪斯'],
                'cat_available':['爱迪斯','爱迪斯','爱迪斯','爱迪斯'],
            },
        }
        """
        setting_data = {}
        setting_data['search_range'] = {}
        # 获取全部公众号列表
        all_gzh_list = list(get_article_metadata().keys())
        all_gzh_list.append('全部')
        all_cat_list = []
        # 获得全部目录列表
        cats = DBQ.get_queue_by_kv(queue_type='公众号分类')
        for cat in cats:
            all_cat_list.append(cat['name'])
        # 获取当前正在使用的搜索范围方式
        try:
            if DBQ('公众号',self.queue_type).get_ext_data()['inuse'] is True:
                current_search_range = '公众号'
            else:
                current_search_range = '类别'
        except Exception as e:
            current_search_range = '公众号'
        # 获得现存搜索范围的公众号列表
        queue = DBQ.get_queue_by_kv(queue_type=self.queue_type,name='公众号')[0]['queue']
        gzh_members = []
        for element in queue:
            gzh_members.append(element['id'])
        gzh_available = sub_list(all_gzh_list, gzh_members)
        # 获得现存范围的类别列表
        queue = DBQ.get_queue_by_kv(queue_type=self.queue_type,name='类别')[0]['queue']
        cat_members = []
        for element in queue:
            cat_members.append(element['id'])
        cat_available = sub_list(all_cat_list, cat_members)

        setting_data['search_range']['current_search_range'] = current_search_range
        setting_data['search_range']['gzh_members'] = gzh_members
        setting_data['search_range']['gzh_available'] = gzh_available
        setting_data['search_range']['cat_members'] = cat_members
        setting_data['search_range']['cat_available'] = cat_available
        return setting_data

    def change_search_range_type(self, range_type):
        """
        :param range_type:范围类型
        :return:更新搜索范围类型
        """
        DBQ('类别',self.queue_type).set_ext_data({'inuse':False})
        DBQ('公众号',self.queue_type).set_ext_data({'inuse':False})
        if range_type == '公众号':
            DBQ('公众号',self.queue_type).set_ext_data({'inuse':True})
        elif range_type == '类别':
            DBQ('类别',self.queue_type).set_ext_data({'inuse':True})
        return self.get_all_settings()

    def delete_from_search_range(self, range_type, name):
        """
        :param range_type:范围类型
        :param name:公众号名称或者类别名称
        :return: 从指定范围中删除元素 操作完成之后更新range_type
        """
        if range_type == '公众号':
            DBQ('公众号',self.queue_type).delete_element({'id':name})
        elif range_type == '类别':
            DBQ('类别',self.queue_type).delete_element({'id':name})
        self.change_search_range_type(range_type)
        return self.get_all_settings()

    def add_to_search_range(self, range_type, name):
        """
        :param range_type:范围类型
        :param name:公众号名称或者类别名称
        :return: 添加元素到指定范围 操作完成之后更新range_type
        """
        if range_type == '公众号':
            gzh_queue = DBQ('公众号',self.queue_type)
            # 如果全部在搜索范围中直接返回
            # if '全部' in self.get_all_settings()['search_range']['gzh_members']:return
            # 如果在全部的公众号中搜索 则队列中只留下'全部'
            if name == '全部':
                gzh_queue.delete_all_element()
            gzh_queue.add_element({'id':name})
        elif range_type == '类别':
            DBQ('类别',self.queue_type).add_element({'id':name})
        self.change_search_range_type(range_type)
        return self.get_all_settings()

    def search_range_data_preprocess(self,gc):
        """
        :parameter gc:GZHCategory实例用于获取存在目录的公众号成员列表
        :return:根据搜索范围设置参数 输出公众号集合列表
        """
        # 按照公众号
        search_range = self.get_all_settings()['search_range']
        if search_range['current_search_range'] == "公众号":
            if '全部' in search_range['gzh_members']:
                return []
            return search_range['gzh_members']
        # 按照分类
        elif search_range['current_search_range'] == "类别":
            gzhs = []
            search_cats = search_range['cat_members']
            all_cats = gc.get_all_cat_data()
            for member in search_cats:
                for cat in all_cats:
                    if member == cat['cat_name']:
                        gzhs = gzhs+cat['cat_members']
                        break
            return list(set(gzhs))
        # 全部
        else:
            return []
