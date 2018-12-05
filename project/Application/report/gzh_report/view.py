from pyecharts import *

def draw_all_mian_date_read(df):
    """
    :param df:
    :return:所有主文章的阅读数据
    """
    bar = Bar('所有发文历史数据')
    bar.add('阅读量', df['date'], df['read'], mark_line=["min", "max", "average"], is_datazoom_show=True, datazoom_type='both')
    bar.add('点赞量', df['date'], df['like'], mark_line=["min", "max", "average"], is_datazoom_show=True, datazoom_type='both')
    bar.add('评论量', df['date'], df['comment'], mark_line=["min", "max", "average"], is_datazoom_show=True, datazoom_type='both')
    bar.add('赞赏量', df['date'], df['reward'], mark_line=["min", "max", "average"], is_datazoom_show=True, datazoom_type='both')
    bar.add('深度指数', df['date'], df['deep_index'], mark_line=["min", "max", "average"], is_datazoom_show=True, datazoom_type='both')
    return bar.get_echarts_options()

def draw_all_statistic(df):
    attr = list(df.index.values)
    bar_50 = Bar("中位数",title_top="5%")
    bar_50.add('阅读', attr, df['read']['50%'], mark_line=["min", "max", "average"])
    bar_50.add('点赞', attr, df['like']['50%'], mark_line=["min", "max", "average"])
    bar_50.add('赞赏', attr, df['reward']['50%'], mark_line=["min", "max", "average"])
    bar_50.add('评论', attr, df['comment']['50%'], mark_line=["min", "max", "average"])

    bar_mean = Bar('平均数',title_top="35%")
    bar_mean.add('阅读', attr, df['read']['mean'], mark_line=["min", "max", "average"])
    bar_mean.add('点赞', attr, df['like']['mean'], mark_line=["min", "max", "average"])
    bar_mean.add('赞赏', attr, df['reward']['mean'], mark_line=["min", "max", "average"])
    bar_mean.add('评论', attr, df['comment']['mean'], mark_line=["min", "max", "average"])


    bar_max = Bar('最大值',title_top="65%")
    bar_max.add('阅读', attr, df['read']['max'], mark_line=["min", "max", "average"])
    bar_max.add('点赞', attr, df['like']['max'], mark_line=["min", "max", "average"])
    bar_max.add('赞赏', attr, df['reward']['max'], mark_line=["min", "max", "average"])
    bar_max.add('评论', attr, df['comment']['max'], mark_line=["min", "max", "average"])

    grid = Grid()
    grid.add(bar_50,grid_top='10%', grid_bottom='70%')
    grid.add(bar_mean, grid_top='40%', grid_bottom='40%')
    grid.add(bar_max, grid_top='70%', grid_bottom='10%')
    # grid.add(bar_count, grid_top='70%', grid_bottom='10%')

    return grid.get_echarts_options()


def draw_dir_posts_num_related(dfd):
    data = {}
    df_mov = dfd['mov']
    bar_mov = Bar('主副文章各自发文总数')
    bar_mov.add('主副文章各自发文总数', df_mov.index.values, df_mov['count'])
    data['mov'] = bar_mov.get_echarts_options()

    df_hour = dfd['hour']
    bar_hour = Bar('不同小时段各自发文总数')
    bar_hour.add('不同小时段各自发文总数', df_hour.index.values, df_hour['count'])
    data['hour'] = bar_hour.get_echarts_options()

    df_week = dfd['week']
    bar_week = Bar('不同星期各自发文总数')
    bar_week.add('不同星期各自发文总数', df_week.index.values, df_week['count'])
    data['week'] = bar_week.get_echarts_options()

    return data

def draw_read_vs_factors(df):
    data = {}
    # 阅读和点赞
    sca_like = Scatter()
    sca_like.add('阅读量和点赞量关系', df['read'], df['like'], is_datazoom_show=True, datazoom_type='both')
    data['like'] = sca_like.get_echarts_options()
    # 阅读和上一次阅读
    sca_pre_read = Scatter()
    sca_pre_read.add('阅读量和上一次阅读量关系', df['read'], df['pre_read'], is_datazoom_show=True, datazoom_type='both')
    data['pre_read'] = sca_pre_read.get_echarts_options()
    return data

def draw_find_best_factors(df):
    data = {}
    # 推文小时
    bar_hour = Bar('发布小时')
    df_hour = df.groupby('hour').describe()['read'][['count','mean','50%']]
    bar_hour.add('总数',df_hour.index.values, df_hour['count'])
    bar_hour.add('平均值',df_hour.index.values, df_hour['mean'])
    bar_hour.add('中位数',df_hour.index.values, df_hour['50%'])
    data['hour'] = bar_hour.get_echarts_options()
    # 推文星期
    bar_week = Bar('发布星期')
    df_week = df.groupby('week').describe()['read'][['count','mean','50%']]
    bar_week.add('总数',df_week.index.values, df_week['count'])
    bar_week.add('平均值',df_week.index.values, df_week['mean'])
    bar_week.add('中位数',df_week.index.values, df_week['50%'])
    data['week'] = bar_week.get_echarts_options()
    # 标题词数
    bar_title = Bar('文章标题字数')
    df_title = df.groupby('title').describe()['read'][['count','mean','50%']]
    bar_title.add('总数',df_title.index.values, df_title['count'])
    bar_title.add('平均值',df_title.index.values, df_title['mean'])
    bar_title.add('中位数',df_title.index.values, df_title['50%'])
    data['title'] = bar_title.get_echarts_options()
    # 插图数量
    bar_pic = Bar('文章插图数')
    df_pic = df.groupby('pic').describe()['read'][['count','mean','50%']]
    bar_pic.add('总数',df_pic.index.values, df_pic['count'])
    bar_pic.add('平均值',df_pic.index.values, df_pic['mean'])
    bar_pic.add('中位数',df_pic.index.values, df_pic['50%'])
    data['pic'] = bar_pic.get_echarts_options()
    # 视频数量
    bar_video = Bar('文章视频数')
    df_video = df.groupby('video').describe()['read'][['count','mean','50%']]
    bar_video.add('总数',df_video.index.values, df_video['count'])
    bar_video.add('平均值',df_video.index.values, df_video['mean'])
    bar_video.add('中位数',df_video.index.values, df_video['50%'])
    data['video'] = bar_video.get_echarts_options()
    return data

def facors_and_read(df):
    scatter = Scatter("阅读数据和其他因素的关系")
    scatter.add("上一次阅读量", df['read'], df['pre_read'], is_datazoom_show=True, datazoom_type='both')
    scatter.add("点赞量", df['read'], df['like'], is_datazoom_show=True, datazoom_type='both')
    scatter.add("标题词数", df['read'], df['title'], is_datazoom_show=True, datazoom_type='both')
    # scatter.render('阅读量因子分析.html')
    return scatter.get_echarts_options()

def draw_average_hour_read(df):
    bar = Bar('小时阅读均值', str(df['count'].sum()))
    bar.add('发文总数', list(df.index.values), df['count'], mark_line=["min", "max", "average"])
    # bar.render('发文最佳时间探索.html')
    return bar.get_echarts_options()
