from tools.dp import Singleton
from es.config import doc_schema, search_template
from copy import deepcopy
from tools.utils import logging
from tools.utils import to_pinyin_full
import re
from instance import es_instance as es
from db import get_collection_article
from elasticsearch import helpers
logger = logging.getLogger(__name__)


class GZHSearch(Singleton):
    """
    管理所有公众号在ES中的index和doc
    """
    def __init__(self):
        self.index_prefix = 'gzh'
        self.doc_type = 'gzh'

    def _index_name(self, nickname):
        """
        :param nickname:
        :return: 根据公众号nickname的拼音产生专用的index名称（暂时没有添拼音相同的处理逻辑）, 先转化为拼音形式再增加前缀
        """
        return self.index_prefix+'_'+(to_pinyin_full(nickname)).lower()

    def get_all_indices(self):
        """
        :return:获取es中公众号相关的所有index
        """
        pass

    def create_index(self,nickname):
        """
        :param nickname:公众号昵称的拼音
        :return:为一个公众号创建index 比如设置字段格式和指定搜索分词器
        在index文档之前应该先mapping index 主要是进行文本分词字段设置
        """
        mapping_body = {}
        mapping_body['properties'] = doc_schema
        index_name = self._index_name(nickname)
        exists = es.indices.exists(index_name)
        if exists is False:
            es.indices.create(index_name)
            es.indices.put_mapping(index=self._index_name(nickname), doc_type=self.doc_type, body=mapping_body)
            logger.info('创建index %s 成功'%(nickname))
        else:
            logger.info('index %s 已经存在'%(nickname))
        return index_name

    def delete_index(self, nickname):
        """
        :param nickname: 公众号昵称的拼音 *删除所有index
        :return:删除index和该index下的所有doc
        """
        if nickname is not "*":
            index_name = self._index_name(nickname)
        es.indices.delete(index_name)

    def index_db_docs(self, nickname):
        """
        :param nickname:公众号昵称
        :return: 从mongodb中获取一个公众号的全部数据 使用bulk操作index进入es
        """
        # 先创建index
        index_name = self.create_index(nickname)
        # 从数据库中获取该公众号的全部文章
        articles = get_collection_article(nickname,article={"$exists": True},title={"$exists": True})
        articles_cache = []
        # mongodb的连接10分钟之后会过期 期间可能会出现完不成index的情况 故先将公众号的全部历史文章缓存
        for article in articles:
            doc = dict((key, article[key]) for key in doc_schema)
            articles_cache.append(doc)
        # 使用bulk操作index文档
        result = self.index_bulk(index_name,articles_cache)
        return result

    def index_docs(self, index_name, doc_dicts):
        """
        :param index_name:
        :param doc_dicts:
        :return:
        """
        for doc_dict in doc_dicts:
            self.index_doc(index_name, doc_dict)

    def doc_exist(self, index_name, doc_dict):
        """
        :param index_name: es中的index名称
        :param doc_dict: 文档体
        :return:文档存在返回1 文档不存在返回0
        """
        # 使用文章的连接判断文档存在与否 存在数量为1 不存在数量为0
        try:
            body = {
                "query":{"match_phrase":{'content_url':doc_dict['content_url']}},
            }
            result = es.count(index=index_name, doc_type=self.doc_type, body=body)['count']
        # 如果公众号对应的index不存在则发生错误 也就说明该文章并未被创建索引
        except :
            result = 0
        return result

    def index_doc(self, index_name, doc_dict):
        """
        :param index_name:es中的index名称
        :param doc_body:文档体
        :return:新建或者更新doc
        """
        doc = dict((key, doc_dict[key]) for key in doc_schema)
        # 当公众号文章更新之后还产生新的文章 直接跳过对旧有文章的index
        if self.doc_exist(index_name, doc_dict) == 1:
            return
        try:
            es.index(index=index_name, doc_type=self.doc_type, id=doc['content_url'], body=doc)
            logger.info('Index %d %s %s'%(doc['article_id'], index_name, doc['title']))
            print('Index %d %s %s'%(doc['article_id'], index_name, doc['title']))
        except:
            logger.warning('index 文档失败:%s %s'%(doc['nickname'], doc['title']))

    def index_bulk(self, index_name, doc_dict_list):
        """
        :param index_name: es中的index名称
        :param doc_dict_list: 文档list doc包含了需要在es中建立索引的字段即可 也可包含更多字段但会过滤掉
        :return:使用bulk进行批量index API会根据指定的_id字段去重 而且支持更新
        """
        if self.index_prefix not in index_name:
            index_name = self._index_name(index_name)
        actions = []
        for doc_dict in doc_dict_list:
            action = {
                "_index": index_name,
                "_type": self.doc_type,
                "_id": doc_dict['content_url'],
                "_source": doc_dict
            }
            actions.append(action)
        result = helpers.bulk(es, actions)
        return result

    def delete_doc(self, nickname, url):
        """
        :param nickname:
        :param url:
        :return: 根据URL删除
        """
        index_name = self._index_name(nickname)
        es.delete(index=index_name, doc_type=self.doc_type,id=url)

    def index_all_db(self):
        from instance.global_instance import weixindb_instance
        from time import time
        gzhs = weixindb_instance.get_all_nickname()
        for nickname in gzhs:
            begin_time = time()
            print("index%s..."%(nickname))
            self.index_db_docs(nickname)
            print("index%s用时%f秒"%(nickname, time()-begin_time))

    def search(self, nicknames, search_data, from_size={"from":0,"size":10}, source=None):
        """
        :param nicknames:公众号昵称列表
        :param search_data:搜索字符串
        :param source:返回数据需要包含的字段
        :return:搜索
        """
        # 根据公众号的昵称
        indices = []
        st = deepcopy(search_template)
        dls = self.search_data_preprocess(search_data)
        st.update(dls)
        if source != None:
            st["_source"] = source
        # 更新from 和 size 支持分页
        try:
            st["from"] = from_size["from"]
            st["size"] = from_size["size"]
        except:
            logger.warning("from_size字段错误 %s"%(str(from_size)))
        if nicknames == []:
            indices = 'gzh*'
        else:
            for nickname in nicknames:
                indices.append(self._index_name(nickname))

        try:
            result = es.search(index=indices, doc_type=self.doc_type, body=st)['hits']
            return result
        except Exception as e:
            logger.critical("搜索错误 可能是有部分公众号没有建立索引%s"%(str(indices)))
            return "ERROR"

    def search_get_all(self,nicknames,search_data,source):
        """
        :param nicknames:
        :param search_data:
        :param fields:
        :return: 返回搜索结果中的全部记录中的自定字段
        """
        total = self.search(nicknames=nicknames, search_data=search_data,from_size={"from":0,"size":1},source=source)["total"]
        # 限制获取的数据量
        if total>=10000:
            total = 10000
        result_data = []
        hits = self.search(
            nicknames=nicknames,
            search_data=search_data,
            from_size={"from":0,"size":total},
            source=source)['hits']
        for hit in hits:
            result_data.append(hit['_source'])
        return result_data

    def search_data_preprocess(self, search_data):
        """
        :param search_data:
        :return: 对即将搜索的数据进行预处理 解析搜索模式
        数据中包含模式：
        双引号包含的内容使用match_phrase全匹配,双引号之外的内容使用分词模式match
        排序模式 指定排序字段以及升降方式
        举例："必须包含词"分词模式-time-1
        根据搜索数据中指定的规则返回查询的query、sort等字段数据
        """
        sort_mapping = {
            "gzh":"nickname",       #公众号昵称
            "loc":"mov",            #文章发布位置
            "author":"author",      #作者
            "time":"p_date",        #发文时间
            "read":"read_num",      #阅读量
            "like":"like",          #点赞量
            "comm":"comments",      #评论量
            "reward":"reward_num",  #赞赏量
            "length":"article_token_len",#文章词数
            "unk":"_score",         #未知 就按照默认的分数排序
        }
        sort_dir_mapping = {
            '0':"asc",
            '1':"desc",
        }
        # 分离搜索数据 排序字段和排序顺序
        if len(re.findall('-',search_data))==2:
            part_data = search_data.split('-')
            try:
                sort_dir = sort_dir_mapping[part_data[-1]]
                sort_field = sort_mapping[part_data[-2]]
            except:
                sort_dir = sort_dir_mapping['1']
                sort_field = sort_mapping['unk']
        else:
            sort_dir = sort_dir_mapping['1']
            sort_field = sort_mapping['unk']
        search_data = search_data.split('-')[0]
        # 找出必须完整包含的字段
        data_match_phrase = [x.replace('"','') for x in re.findall(r'"\S*?"', search_data)]
        data_match = search_data.replace('"','')
        # 创建必须完整包含字段的Elsticsearch搜索描述数据
        for x in data_match_phrase:
            data_match = data_match.replace(x,'').replace(' ','')
        query_value = {
            "bool": {
                "must": []
            }
        }
        match_phrase_item = {
            "match_phrase": {"article": ""}
        }
        match_item = {
            "match": {"article": ""}
        }
        # 创建分词字段 英文不分词根据空格
        if data_match != '':
            match_item["match"]["article"] = data_match
            query_value["bool"]["must"].append(deepcopy(match_item))
        for item in data_match_phrase:
            match_phrase_item["match_phrase"]["article"]=item
            query_value["bool"]["must"].append(deepcopy(match_phrase_item))

        sort_value = [
            {
                sort_field: {
                    "order": sort_dir
                }
            }
        ]
        return {"query":query_value,"sort":sort_value}
