// 和服务器进行数据通信绑定

console.log('创建wobsocket 通信')
var socket = io.connect('http://localhost:5000');

// 绑定和服务器连接成功信息
socket.on('connect', function() {
    socket.emit('connected replay', { data: 'I\'m connected!' });
});

// 手机爬虫状态
socket.on('phone_crawler_data', function(data) {
    vm_phone_crawler_data.crawlers = data
});

// 显示当前的爬取文章队列
socket.on('articles_logger_monitoring', function(data) {
    //添加一个颜色属性
    vm_articles_logger_monitoring.articles = data
});

// 数据库中的所有公众号列表数据更新
socket.on('gzhs_list_data', function(data) {
    vm_gzhs_list_data.gzhs = data
});

// 正在执行爬取任务的公众号列表数据更新
socket.on('gzhs_todolist_data', function(data) {
    vm_gzhs_todolist_data.gzhs = data
});

// 公众号分类数据更新
socket.on('gzh_category', function(data) {
    vm_app_gzh_category_data.category = data
});
