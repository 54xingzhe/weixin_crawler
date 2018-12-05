from tools.data_queue import DBQ
from db.meta_data import get_article_metadata
from tools.utils import sub_list


class GZHCategory():
    """
    管理公众号分类 接受前端的消息对对数据进行组织并反馈结果给前端
    """
    def __init__(self, queue_type='公众号分类'):
        self.queue_type = queue_type

    def get_all_cat_data(self):
        """
        :return:返回当前的所有分类数据, 温和前端的数据格式
        """
        category = []
        # 获得数据库中所有公众号的名称为添加选项做准备
        gzh_list = list(get_article_metadata().keys())
        # 获得分类名称和该分类下的所有公众号
        queue = DBQ.get_queue_by_kv(queue_type=self.queue_type)
        for cat in queue:
            data = {}
            data['cat_name'] = cat['name']
            data['cat_members'] = []
            for mem in cat['queue']:
                data['cat_members'].append(mem['id'])
            # 找出不在分类中的公众号作为待加入选项
            # data['cat_available'] = [x for x in gzh_list if x not in data['cat_members']]
            data['cat_available'] = sub_list(gzh_list, data['cat_members'])
            category.append(data)
        return category

    def add_cat(self, cat_name):
        """
        :param cat_name:分类名称
        :return: 添加一个分类
        """
        DBQ(cat_name,self.queue_type)
        return self.get_all_cat_data()

    def delete_cat(self, cat_name):
        """
        :param cat_name: 分类名称
        :return:删除一个分类
        """
        DBQ.delete_queue(cat_name,self.queue_type)
        return self.get_all_cat_data()

    def add_cat_gzh(self, nickname, cat_name):
        """
        :param nickname:公众号昵称
        :param cat_name:分类名称
        :return:在指定分类中增加一个公众号
        """
        cat = DBQ(name=cat_name,queue_type=self.queue_type)
        cat.add_element({'id':nickname})
        return self.get_all_cat_data()

    def delete_cat_gzh(self, nickname, cat_name):
        """
        :param nickname:公众号昵称
        :param cat_name: 分类名称
        :return:从指定分类中删除一个公众号
        """
        cat = DBQ(name=cat_name,queue_type=self.queue_type)
        cat.delete_element({'id':nickname})
        return self.get_all_cat_data()
