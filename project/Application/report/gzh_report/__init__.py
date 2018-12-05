from db import get_collection_article
from Application.report.gzh_report.GZH import GZH
from Application.report.gzh_report.view import *
from Application.report.gzh_report.utils import df2table
from jinja2 import Template


class GZHReportData():
    """
    产生公众号报告所需要的数据
    """
    def __init__(self, nickname):
        """
        :param nickname: 公众号名称
        """
        self.nickname = nickname
        # 生成器转化成为list 赋值给self.posts
        self.posts = []
        self.total_num = 0
        self.crawled_num = 0
        self.uncrawled_num = 0
        for p in get_collection_article(nickname):
            # 过滤掉没有爬取阅读数据的文章
            if 'read_num' in p:
                self.posts.append(p)
                self.crawled_num += 1
            else:
                self.uncrawled_num += 1
            self.total_num += 1
        #
        if self.crawled_num != 0:
            self.gzh = GZH(self.posts)
            self.gzh.postsToDataframe()
            # echarts的option_data
            self.option_data = {}
            # 公众号名称
            self.option_data['account_name'] = nickname
            # 累计发文总数
            self.option_data['posts_info'] = ' 有效文章%d 其中%d具有阅读数据 还剩%d尚无阅读数据'%\
                                                  (self.total_num,self.crawled_num,self.uncrawled_num)

    def _add_option_data(self):
        """
        :return:将公众号表格中需要的数据逐个添加到self.option_data
        """
        # 历史所有文章阅读数据
        df = self.gzh.allMainDateRead()
        all_mian_date_read = draw_all_mian_date_read(df)
        self.option_data['all_mian_date_read'] = all_mian_date_read

        # 主副文章统计数据
        df = self.gzh.allStatistic()
        all_statistic = draw_all_statistic(df)
        self.option_data['all_statistic'] = all_statistic

        # 不同主副/小时/星期类别文章发文数量统计
        dfd = self.gzh.dirPostsNumRelated()
        dir_posts_num_related  = draw_dir_posts_num_related(dfd)
        self.option_data['dir_posts_num_related'] = dir_posts_num_related

        # 阅读量分别和点赞量/上一次阅读量之间的关系
        df = self.gzh.factorsAndRead()
        self.option_data['read_vs_factors'] = draw_read_vs_factors(df)
        # 探索最佳推文小时 推文星期 标题词数 插图数量 视频数量
        self.option_data['find_best_factors'] = draw_find_best_factors(df)

        # 文章列表数据
        self.option_data['table'] = {}
        # 表9 100001除外阅读来那个最高的10篇文章
        df = self.gzh.getNumNExcept(mov='all')
        self.option_data['table']['particular_most_read_10_except_100001'] = df2table(df, ['like','点赞量'])
        # 表10 阅读量最低且为非0的10篇文章
        df = self.gzh.getNumNExcept(com='read', exce=0, asc=1)
        self.option_data['table']['particular_least_read_10_except_0'] = df2table(df, ['like','点赞量'])
        # 表11 深度指数最高的10篇文章.
        df = self.gzh.getNumN(com='deep_index')
        self.option_data['table']['particular_most_deep_10'] = df2table(df, ['deep_index','深度指数'])
        # 表12 深度指数最低的10篇文章
        df = self.gzh.getNumN(com='deep_index', asc=1)
        self.option_data['table']['particular_least_deep_10'] = df2table(df, ['deep_index','深度指数'])
        # 表13 落差指数最低的10篇文章
        df = self.gzh.getNumN(com='fall_index', asc=1)
        self.option_data['table']['particular_least_fall_10'] = df2table(df, ['fall_index','落差指数'])
        # 表14 所有的100001文章
        df = self.gzh.getNumCondition(mov='all')
        self.option_data['table']['particular_all_10001'] = df2table(df, ['like','点赞量'])

    def create_js(self):
        """
        :param des_dir:产生js文件的存储位置
        :return:js文件名
        """
        from time import time
        self._add_option_data()
        js_name = 'cache_'+str(time())
        js_file = r"ui/static/auto_created_js/"+js_name+'.js'
        # 打开模板文件
        with open(r'ui/templates/option_data.js','r',encoding='utf8') as f:
            template = Template(f.read())
        # 使用self.option_data渲染js模板文件option_data.js
        option_data_js = template.render(data=self.option_data)
        # 保存渲染后的option_data.js
        with open(js_file,'w',encoding='utf8') as f:
            f.writelines(option_data_js)
        return option_data_js,'auto_created_js/'+js_name+'.js'
