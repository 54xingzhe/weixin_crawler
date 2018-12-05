console.log('创建wobsocket 通信')
var socket = io.connect('http://localhost:5000');

//记录当前请求页面信息
var search_result_page_info ={
    "pre_search_data":'',
    "cur_search_data":'',
    "total":0,
    "from":0,
    "size":10,
    "current":0,
}

//记录点击显示搜索指数图表次数
var search_result_index_btn_flag = 0

//收索结果指数配置
var search_index_result_option = {
    title:{
        text:'正在计算...'
    }
};

$('.search_result').find('*').css({'margin':0})
$( "#search_input" ).keyup(function(event) {
    // Cancel the default action, if needed
    // event.preventDefault();
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) {
        var search_data = $('#search_input').val();
        // 只有当本次搜索数据发生变化之后才更新上一次搜索数据为赋值前的本次搜索数据
        if(search_result_page_info.cur_search_data != search_data){
            search_result_page_info.pre_search_data = search_result_page_info.cur_search_data
        }
        search_result_page_info.cur_search_data = search_data
        search_result_page_info.current = 1
        // $.post('http://localhost:5000/search_gzh', search_data)
        socket.emit('search_gzh',{'search_data':search_data,'page_info':search_result_page_info})
        // 搜索次数清零
        search_result_index_btn_flag = 0
        search_index_result_option.title.text = "正在计算..."
        search_index_result.setOption(search_index_result_option);
    }
});

//搜索结果返回
var vm_search_data_result_data = new Vue({
    el:'#vm-app-search-result-data',
    data:{
        result:{
            "total":'',
            "data":[]
        }
    }
})

// 搜索结果数据
socket.on('search_reult_page', function(data) {
    vm_search_data_result_data.result = data
    search_result_page_info.total = data["total"]
    // 更新页码信息
    $('#pages_info')[0].innerText=String(search_result_page_info.current)+'/'+String(Math.ceil(search_result_page_info.total/search_result_page_info.size))
    // 由于没有跟新整个页面 自动回到页面页面顶部
    $("html, body").animate({ scrollTop: 0 }, "fast")
});

// 打开搜索设置
$('#search_setting_btn').click(function (evt) {
    $('#search_setting_pannel').css("display", "block");
})

// 搜索结果下一页
$('#next_page').click(function (evt) {
    if(search_result_page_info.current >= Math.ceil(search_result_page_info.total/search_result_page_info.size)){
        alert("已经是最后一页")
        return
    }
    search_result_page_info.from += search_result_page_info.size
    search_result_page_info.current += 1
    socket.emit('search_gzh',{
        'search_data':search_result_page_info.cur_search_data,
        'page_info':search_result_page_info})
})

// 搜索结果上一页
$('#pre_page').click(function (evt) {
    // 已经是第一页 直接返回
    if(search_result_page_info.current == 1){
        alert("已经是第1页")
        return
    }
    search_result_page_info.from -= search_result_page_info.size
    search_result_page_info.current -= 1
    socket.emit('search_gzh',{
        'search_data':search_result_page_info.cur_search_data,
        'page_info':search_result_page_info})
})

// 定义搜索结果指数图表
var search_index_result = echarts.init(document.getElementById('search_result_index_chart'));
search_index_result.setOption(search_index_result_option);
// 显示搜索结果指数
$("#search_result_index_btn").click(function (evt) {
    var chart_display_type = "block"
    if(search_result_index_btn_flag%2==1){
        $("#search_result_index_chart").css({"display":"block"})
    }
    else{
        $("#search_result_index_chart").css({"display":"none"})
    }
    search_result_index_btn_flag++
    console.log(search_result_index_btn_flag)
    if(search_result_index_btn_flag == 1){
        //第一次显示指数图表 后台发送请求 超过10000搜索结果仅统计前10000条结果
        if(search_result_page_info.total <= 10000){
            search_result_page_info.total = 10000
        }
        socket.emit('search_result_index',search_result_page_info)
    }
})

socket.on("search_result_index",function (data) {
    console.log(typeof(data))
    search_index_result_option = JSON.parse(data)
    search_index_result.setOption(search_index_result_option);
})
