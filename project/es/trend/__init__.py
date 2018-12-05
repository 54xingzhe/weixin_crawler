import pandas as pd
from datetime import datetime
from tabulate import tabulate
from pyecharts import Bar


def articles_and_time(raw_data, time_gap='month'):
    """
    :param raw_data:来自search_get_all的返回数据
    :param time_gap:时间间隔 天 月 年三种单位
    :return:计算指定时间间隔内的文章数量 并生成二维数据用作图表可视化
    """
    time_gap_mapping = {
        'year':['year'],
        'month':['year','month'],
        'day':['year','month','day'],
    }
    df = pd.DataFrame(columns=['year', 'month', 'day','week','tag'])
    for i in range(len(raw_data)):
        date_time = datetime.strptime(raw_data[i]['p_date'],'%Y-%m-%dT%H:%M:%S')
        row = p_date_extract(date_time)
        row.append(1)
        df.loc[i] = row
    df = df.groupby(time_gap_mapping[time_gap])[['tag']].describe(percentiles=[.5])
    # df分组之后抽取出纵坐标的参数
    y_data_list = df['tag']['count'].tolist()
    # df分组之后抽取出横坐标的参数
    x_data_list =['-'.join(x) for x in list(df.index.values)]
    return x_data_list,y_data_list

def draw_bar(x, y, title):
    attr = x
    bar_index = Bar("指数",title_top="5%")
    bar_index.add(title, attr, y, mark_line=["min", "max", "average"])
    return bar_index.get_echarts_options()

def p_date_extract(p_date):
    """
    :param p_date: datetime实例
    :return:['年','月','日','星期']
    """
    date = p_date.strftime("%Y-%m-%d").split('-')
    date.append(str(p_date.weekday()+1))
    return date

if __name__ == "__main__":
    from datetime import datetime
    date = p_date_extract(datetime.strptime('2018-11-03T19:20:09','%Y-%m-%dT%H:%M:%S'))
    print(date)
