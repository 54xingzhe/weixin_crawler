from ui.ui_instance import app, socketio, the_redis
from Application.gzh_category import GZHCategory
from Application.gzh_crawler import GZHCrawler
from es.setting import  GZHSearchSetting

# 公众号爬虫应用实例
gc = GZHCrawler()
# 公众号类别管理实例 主要服务于定向搜索
gzh_category = GZHCategory()
# 搜索设置实例 主要服务于对搜索行为的设置
gzh_setting = GZHSearchSetting()


def run_webserver():
    socketio.run(app, host= '0.0.0.0')

def run_gzh_crawler():
    import time
    while True:
        # 增加时间等待防止CPU使用率过高
        time.sleep(1)
        gc.run()


# 延迟import是为了防止递归import
from ui.router import *
from ui.event import *


