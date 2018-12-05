from tools.data_queue import RQ
from tools.data_queue import DBQ
from phone_operate.WeixinOperate import WeixinOperate
from configs.crawler import adb_ports

class GZHCrawler():
    """
    只有一个实例对象，在设计模式中可以采用单例模式
    接受一个公众号爬虫管理者实例作为参数
    """
    def __init__(self):
        self.gzh_task_rq = RQ('gzh_task_rq')
        self.phone_adb_dbq = DBQ('phone_adb_ports','爬虫')
        self.report_crawling_items = []
        # 讲设置文件中的adb端口存入爬虫队列
        for adb in adb_ports:
            self.phone_adb_dbq.add_element({'id':adb,'nick_name':'未知','wxuin':'未知'})

    def report_gzh_finished(self):
        """
        :return:产生数据报告所有公众号的状态 名称 更新时间 等信息
        [{nickname,article_num,update_time,update_num}{}{}]
        report一次需要单独计算机每一个collection中的文档数量 优秀浪费时间 方法待改进
        """
        # 获取mongdb中的公众号的状态
        report = {}
        report_data = []
        from db.meta_data import get_article_metadata
        from db import count
        meta_data = get_article_metadata(all=False)
        total_article = 0
        for key in meta_data:
            unit = {}
            unit['nickname'] = key
            unit['article_num'] = count(key)
            unit['update_time'] = meta_data[key]['date'].strftime("%Y/%m/%d %H:%M")
            unit['update_num'] = meta_data[key]['articles_num']
            report_data.append(unit)
            total_article += unit['article_num']
        report['data'] = report_data
        report['meta'] = {}
        report['meta']['total_gzh'] = len(report_data)
        report['meta']['total_article'] = total_article
        return report

    def _report_gzh_doing(self):
        """
        :return:产生数据报告正在进行任务的公众号状态
        数据来自任务队列 任务队列中存在的公众号和当前正在处理的公众号
        nickname,percent,begin_time,need_time
        """
        report_data = []
        from tools.utils import dictstr_to_dict
        # 队列中需要处理的公众号
        gzh_need_todolist = self.gzh_task_rq.get_rq_data()
        for gzh in gzh_need_todolist:
            gzh_task = dictstr_to_dict(gzh)
            unit = {}
            unit['nickname'] = gzh_task['nickname']
            unit['percent'] = 'UNK/UNK'
            unit['begin_time'] = 'UNK'
            unit['need_time'] = 'UNK'
            report_data.append(unit)
        return report_data

    def report_crawler(self):
        adb_ports = self.phone_adb_dbq.get_queue()
        report_data = []
        for adb in adb_ports:
            unit = {}
            unit['adb_port'] = adb['id']
            unit['nick_name'] = adb['nick_name']
            unit['wxuin'] = adb['wxuin']
            report_data.append(unit)
        return report_data

    def report_gzh_doing(self):
        """
        :return:当前可能并未任务
        """
        try:
            report_data = self._report_gzh_doing()
        except:
            report_data = []
        return report_data

    def add_crawler(self,crawler):
        """
        :param self:
        :return:添加爬虫
        """
        self.phone_adb_dbq.add_element({'id':crawler['phone'],'nick_name':'未知','wxuin':'未知'})

    def delete_crawler(self,crawler):
        """
        :param crawler:
        :return:删除爬虫
        """
        print(crawler)
        self.phone_adb_dbq.delete_element({'id':crawler['phone']})

    def report_crawling(self,item,num=15):
        """
        :param num: 日志条数
        :param item:{'nickname':**,'percent':'12/1231','speed':0.023,'title':'***'}
        :return:
        """
        from ui.ui_instance import socketio
        self.report_crawling_items = [item] + self.report_crawling_items
        if len(self.report_crawling_items)>num:
            self.report_crawling_items.pop()
        socketio.emit('articles_logger_monitoring',self.report_crawling_items)
        return self.report_crawling_items


    def add_gzh(self,gzh):
        """
        :param gzh:
        :return:添加公众号 到任务队列
        """
        self.gzh_task_rq.push(gzh)

    def delete_gzh(self,gzh):
        """
        :param gzh:
        :return:删除公众号
        """
        pass

    def update_gzh(self,gzh,n):
        """
        :param gzh:
        :return: 更新公众号文章
        """
        pass

    def gzh_report(self,gzh):
        """
        :param gzh:
        :return:生成公众号历史文章数据报告
        """
        pass

    def gzh_article_list(self,gzh):
        """
        :param gzh:
        :return: 生成公众号的所有文章列表
        """
        pass

    def export_excel(self,gzh,field):
        """
        :param gzh:
        :param field:
        :return:公众号的指定字段到处到excel
        """
        pass

    def run(self):
        """
        :return:新加入的爬虫每当接到文章爬取任时就会自动获取请求参数
        公众号爬虫的整个生命周期中都需要有一个后台进程监控公众的的爬取任务和更新任务
        run需要在一个进程中不停执行
        """
        # 爬取任务
        from tools.utils import dictstr_to_dict
        gzh_task = self.gzh_task_rq.pop()
        if gzh_task == []:
            return
        gzh_task = dictstr_to_dict(gzh_task)
        self.gzh_in_service = gzh_task['nickname']
        print(gzh_task)
        # 获取参数
        adb_ports_raw = self.phone_adb_dbq.get_queue()
        adb_ports = []
        for adb in adb_ports_raw:
            adb_ports.append(adb['id'])
        wo = WeixinOperate(adb_ports)
        if gzh_task['aom'] == 'halfauto':
            wo.get_all_req_data(gzh_task['nickname'], hand=True)
        elif gzh_task['aom'] == 'auto':
            wo.get_all_req_data(gzh_task['nickname'], hand=False)
        # 调用爬虫
        from crawler import run_crawl
        config = int(gzh_task['range'])
        # from os import system
        # system('python run_crawler.py '+str(config))
        run_crawl(config)
