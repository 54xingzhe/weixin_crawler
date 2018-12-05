import re

def df2table(df, attr):
    '''
    attr是表格独自列的英文名称和中文名称,例如:['name','名字']
    英文名称用于索引df 中文名称用于表格标题
    '''
    table_data = {}
    table_data['attribute'] = attr[1]
    table_data['data'] = []
    id = 0
    for index,row in df.iterrows():
        id += 1
        data_content = {}
        data_content['id'] = id
        # 之所以要使用正则表达式去除标题中的`是因为在js文件中将使用``表示多行字符串
        data_content['title_cnt'] =  re.sub(r'`','',row.title_cnt)
        data_content['url'] = row.url
        data_content['read'] = row.read
        data_content['like'] = row.like
        data_content['date'] = row.date
        if attr[0]!='read' : data_content['attribute'] = row[attr[0]]
        if attr[0]!='like' : data_content['attribute'] = row[attr[0]]
        table_data['data'].append(data_content)
    return table_data
