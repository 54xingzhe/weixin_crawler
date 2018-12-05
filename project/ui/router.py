from ui.ui_instance import app
from flask import render_template


@app.route('/', methods=['GET'])
def index():
    return render_template('index/index.html', data={'title':'公众号采集'})

@app.route('/search', methods=['GET'])
def search():
    return render_template('search/index.html', data={'title':'AII搜索'})

@app.route('/flush_req_data', methods=['GET'])
def flush_req_data():
    from crawler_assist.tidy_req_data import TidyReqData
    TidyReqData.flush_data("*.req")
    return "缓存的请求数据已经删除"

@app.route('/restart', methods=['GET'])
def restart():
    from tools import restart
    restart()

@app.route('/gzh_article_list/<nickname>', methods=['GET'])
def gzh_article_list(nickname):
    from Application.report.AllArticles import get_all_articles_data
    data = get_all_articles_data(nickname)
    return render_template('report/all_articles.html', data=data)


@app.route('/gzh_report/<nickname>', methods=['GET'])
def gzh_report(nickname):
    from Application.report.gzh_report import GZHReportData
    grd = GZHReportData(nickname)
    if grd.crawled_num==0:
        return nickname+"尚无阅读数据 请先爬取"
    _,js_file_name = grd.create_js()
    return render_template('report/gzh_report.html', data={'title':nickname,'js':js_file_name})

