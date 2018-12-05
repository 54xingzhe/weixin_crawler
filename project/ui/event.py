from ui.ui_instance import socketio
from ui import gc,gzh_category,gzh_setting
from tools.utils import str_to_dict,debug_p
from instance.global_instance import gs


@socketio.on('my_event')
def handle_message(json):
    print('received message: ' + str(json))
    return 'frank'


@socketio.on('connect')
def handle_message_connected():
    # 公众号分组设置
    cat_data = gzh_category.get_all_cat_data()
    socketio.emit('gzh_category',cat_data)
    # 搜索设置
    search_setting_data = gzh_setting.get_all_settings()
    socketio.emit('search_setting',search_setting_data)
    # 已经完成的公众号
    report_data = gc.report_gzh_finished()
    socketio.emit('gzhs_list_data',report_data)
    # 爬虫信息
    report_data = gc.report_crawler()
    socketio.emit('phone_crawler_data',report_data)


# 搜索
@socketio.on('search_gzh')
def search_gzh(data):
    search_data = data['search_data']
    page_info = data['page_info']
    from es.view import search_result_pretty
    # 根据设置找出需要搜索的公众号列表
    nicknames = gzh_setting.search_range_data_preprocess(gzh_category)
    result = gs.search(nicknames=nicknames ,search_data=search_data, from_size=page_info)
    if result == "ERROR":
        return
    result = search_result_pretty(result)
    socketio.emit('search_reult_page',result)


# 添加公众号
@socketio.on('gzhs_todolist_add')
def on_gzhs_todolist_add(data):
    data = str_to_dict(data,'&','=')
    gc.add_gzh(data)
    report_data = gc.report_gzh_doing()
    socketio.emit('gzhs_todolist_data',report_data)


# 添加手机微信爬虫
@socketio.on('phone_crawler_add')
def on_phone_crawler_add(data):
    data = str_to_dict(data,'&','=')
    gc.add_crawler(data)
    report_data = gc.report_crawler()
    socketio.emit('phone_crawler_data',report_data)


# 删除手机微信爬虫
@socketio.on('phone_crawler_delete')
def on_phone_crawler_add(data):
    gc.delete_crawler(data)
    report_data = gc.report_crawler()
    socketio.emit('phone_crawler_data',report_data)

# 添加公众号类别
@socketio.on('add_gzh_category')
def add_gzh_category(data):
    cat_name = data
    cat_data = gzh_category.add_cat(cat_name=cat_name)
    socketio.emit('gzh_category',cat_data)


# 删除类别
@socketio.on('delete_gzh_category')
def delete_gzh_category(data):
    cat_name = data
    cat_data = gzh_category.delete_cat(cat_name=cat_name)
    socketio.emit('gzh_category',cat_data)


# 公众号类别添加公众号
@socketio.on('add_gzh_to_category')
def add_gzh_to_category(data):
    cat_name_raw = data['cat_name_raw']
    nickname = data['nickname']
    import re
    # 前端select界面直接获取cat_name费劲 直接讲innerhtml 传递给后端 分析出cat_name
    cat_name = re.findall(r'data-category="\S*?">',cat_name_raw)[0].split('"')[1]
    cat_data = gzh_category.add_cat_gzh(cat_name=cat_name, nickname=nickname)
    socketio.emit('gzh_category',cat_data)


# 删除类别公众号
@socketio.on('delete_gzh_from_category')
def delete_gzh_from_category(data):
    cat_name = data['cat_name']
    nickname = data['nickname']
    cat_data = gzh_category.delete_cat_gzh(cat_name=cat_name, nickname=nickname)
    socketio.emit('gzh_category',cat_data)


# 删除搜索范围元素
@socketio.on('search_setting_delete_from_search_range')
def search_setting_delete_from_search_range(data):
    range_type = data['range_type']
    element_name = data['element_name']
    search_setting_data = gzh_setting.delete_from_search_range(range_type=range_type,name=element_name)
    socketio.emit('search_setting',search_setting_data)


# 增加搜索范围元素
@socketio.on('search_setting_add_to_search_range')
def search_setting_add_to_search_range(data):
    range_type = data['range_type']
    element_name = data['element_name']
    search_setting_data = gzh_setting.add_to_search_range(range_type=range_type,name=element_name)
    socketio.emit('search_setting',search_setting_data)


# 改变范围类型
@socketio.on('search_setting_change_range_type')
def search_setting_change_range_type(data):
    range_type = data['range_type']
    search_setting_data = gzh_setting.change_search_range_type(range_type)
    socketio.emit('search_setting',search_setting_data)


# 请求当前搜索数据的指数图表option数据
@socketio.on('search_result_index')
def search_result_index(data):
    search_data = data['cur_search_data']
    # 根据设置找出需要搜索的公众号列表
    nicknames = gzh_setting.search_range_data_preprocess(gzh_category)
    data = gs.search_get_all(nicknames,search_data,source=['p_date'])
    from es.trend import articles_and_time,draw_bar
    x,y = articles_and_time(raw_data=data)
    chart_option = draw_bar(x,y,search_data)
    socketio.emit("search_result_index",chart_option)


def refresh_report_data():
    import time
    while True:
        # 已经完成的公众号
        # report_data = gc.report_gzh_finished()
        # socketio.emit('gzhs_list_data',report_data)
        # 正在处理的公众号
        report_data = gc.report_gzh_doing()
        socketio.emit('gzhs_todolist_data',report_data)
        # 爬虫信息
        report_data = gc.report_crawler()
        socketio.emit('phone_crawler_data',report_data)
        time.sleep(1)
