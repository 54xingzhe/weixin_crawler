import pandas as pd


class GZH:
    """
    解析从数据库中直接得到的公众号原始数据 组织数据方便后续公众号报告中使用
    """
    def __init__(self, posts):
        self.posts = posts
    def postsToDataframe(self,features='all'):
        id = 0
        posts_df = []
        for p in self.posts:
            data = []
            data.append(id)
            data.append(p['title'])
            data.append(p['content_url'])
            data.append(p['p_date'].strftime('%Y/%m/%d'))
            data.append(int(p['p_date'].strftime('%Y')))
            data.append(int(p['p_date'].strftime('%m')))
            data.append(int(p['p_date'].strftime('%d')))
            data.append(int(p['p_date'].strftime('%H')))
            data.append(p['p_date'].weekday()+1)
            data.append(p['pic_num'])
            data.append(p['video_num'])
            data.append(p['read_num'])
            data.append(p['like_num'])
            data.append(p['reward_num'])
            data.append(p['comment_num'])
            data.append(p['author'])
            data.append(int(p['mov']))
            data.append(len(p['title']))
            id += 1
            posts_df.append(data)
        # 生成DataFrame方便计算
        self.posts_df = pd.DataFrame(posts_df)
        # DataFrame数据列重命名
        self.posts_df.rename(columns={0:'id',           # 文章编号
                                      1:'title_cnt',    # 标题内容
                                      2:'url',          # 文章连接
                                      3:'date',         # 发文日期
                                      4:'year',         # 发文年
                                      5:'month',        # 发文月
                                      6:'day',          # 发文日
                                      7:'hour',         # 发文小时
                                      8:'week',         # 发文星期
                                      9:'pic',         # 文章插图数
                                      10:'video',       # 文章视频数
                                      11:'read',        # 文章阅读量
                                      12:'like',        # 文章点赞量
                                      13:'reward',      # 文章赞赏量
                                      14:'comment',     # 文章评论量
                                      15:'author',      # 作者
                                      16:'mov',         # 发文位置(主副 main or vice)
                                      17:'title',       # 文章标题
                                      } ,inplace=True)
        # 深度指数 点赞/阅读*1000
        self.posts_df['deep_index'] = round((self.posts_df['like']/self.posts_df['read'])*1000,2)
        self.posts_df.fillna(method='ffill', inplace=True)
        return self.posts_df

    def allStatistic(self):
        '''
        针对主副文章分别做统计，返回的dataframe的collum有两层深度第一层是主副（发文位置）第二层是统计数字
        '''
        # 计算机A各项指标的平均值
        df_move = self.posts_df.groupby('mov')[['read','like','reward','comment']].describe(percentiles=[.5])
        return df_move

    def allMainDateRead(self):
        '''
        返回所有主文章的阅读数据 落差指数仅仅针对主文章有意义
        '''
        main_posts_df = self.posts_df.loc[self.posts_df['mov']==10][['id','title_cnt','url','date','read','like','comment','reward','deep_index']]
        # 加入上一次文章的阅读量
        main_posts_df['pre_read'] = main_posts_df.read.shift(-1)
        # 落差指数 上次阅读量/本次阅读量*1000
        main_posts_df['fall_index'] = round((main_posts_df['pre_read']/main_posts_df['read'])*1000,2)
        # 按发文时间降序排序
        return main_posts_df.sort_values(by='date',ascending=False)

    def dirPostsNumRelated(self):
        '''
        返回各类文章在阅读量上的统计数字 明确50%作为中位数
        '''
        dfd = {}
        dfd['mov'] = self.posts_df.groupby('mov').describe(percentiles=[.5])['read']
        dfd['week'] = self.posts_df.groupby('week').describe(percentiles=[.5])['read']
        dfd['hour'] = self.posts_df.groupby('hour').describe(percentiles=[.5])['read']
        return dfd

    def factorsAndRead(self):
        '''
        将posts中可能和阅读量有关的所有因素返回,建议使用散点图表示
        '''
        main_posts_df = self.posts_df.loc[self.posts_df['mov']==10][['id','read','like','title','pic','video','week','hour']]
        # 加入上一次文章的阅读量
        main_posts_df['pre_read'] = main_posts_df.read.shift(-1)
        # 落差指数 上次阅读量/本次阅读量*1000
        main_posts_df['fall_index'] = round((main_posts_df['pre_read']/main_posts_df['read'])*1000,2)
        return main_posts_df

    def averageHourRead(self):
        '''
        一天中的不同小时段发文数量并不相同,仅仅比较发文总数,和总阅读量无法评估每个小时段对应的单位效果
        应该采用该时段的平均阅读量=阅读总量/发文数量
        建议使用条形图展示
        '''
        return self.posts_df.groupby('hour').describe(percentiles=[.5])['read']

    def getNumN(self,com='read',n=10, asc=0, mov='main'):
        '''
        返回指定字段最高或最低的n行
        '''
        if com == 'fall_index':
            df = self.allMainDateRead()
        else:
            df = self.posts_df
        if mov=='main' and com!='fall_index':df = df.loc[df['mov']==10]
        # 按照阅读量进行降序排序
        df2 = df.sort_values([com],ascending=asc)
        return df2.loc[df2.index[0:n]]

    def getNumNExcept(self,com='read',exce=100001,n=10, asc=0, mov='main'):
        '''
        返回指定字段最高或最低的n行
        '''
        df = self.posts_df.loc[self.posts_df[com] != exce]
        if mov=='main':df = df.loc[df['mov']==10]
        # 按照阅读量进行降序排序
        df2 = df.sort_values([com],ascending=asc)
        return df2.loc[df2.index[0:n]]

    def getNumCondition(self,com='read',thr=100001,dir='==', mov='main'):
        '''
        返回指定字段最高或最低的n行
        '''
        df = self.posts_df
        if mov=='main':df = df.loc[df['mov']==10]
        if dir=='!=':return df.loc[df[com] != thr]
        elif dir=='>=':return df.loc[df[com] >= thr]
        elif dir=='<=':return df.loc[df[com] <= thr]
        elif dir=='>':return df.loc[df[com] > thr]
        elif dir=='<':return df.loc[df[com] < thr]
        else:return df.loc[df[com] == thr]

    def getRwaDatarame(self):
        '''
        返回原始的数据集合,自己编写搜索规则
        # 某个属性包含多个值中的一个
        df2.loc[df2['hour'].isin([21,20])]
        # 多个条件
        df2.loc[(df2.hour==21) & (df2.read>=20000)]
        # 指定需要返回的collumes
        df2.loc[(df2.hour==21) & (df2.read>=20000),['like','hour']]
        '''
        return self.posts_df
