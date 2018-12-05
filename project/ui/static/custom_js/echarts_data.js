//jinjia现将数据存放在html某个元素的data属性中 获取数据 定义echarts对象 设置数据 数据为string需要转为object
var data = $('#my_playlist_data').data('tempalte');
data = JSON.parse(data)
var all_his_bar = echarts.init(document.getElementById('all_main_message'));
all_his_bar.setOption(data);

//添加条形图点击事件
function eConsole(param) {
    if (typeof param.seriesIndex != 'undefined') {
        var url_data = {};
        url_data['data_type'] = param.seriesName;
        url_data['data'] = param.data;
        url_data['date'] = param.name;
        url_data['url'] = decodeURIComponent(location.href,true);
        console.log(url_data);
        $.post('http://localhost:5000/raw_article', (url_data));
    }
}

all_his_bar.on('click', eConsole);
all_his_bar.on('dblclick', eConsole);
