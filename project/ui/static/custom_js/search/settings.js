// 搜索设置
// 定义初始搜索设置数据
var search_setting_data = {
    'search_range':{
        'current_search_range':'类别',
        'gzh_members':['爱迪斯1','爱迪斯2','爱迪斯3','爱迪斯4'],
        'gzh_available':['爱迪斯5','爱迪斯6','爱迪斯7','爱迪斯8'],
        'cat_members':['教育1','教育2','教育3','教育4'],
        'cat_available':['教育5','教育6','教育7','教育8'],
    },
}

// 搜索范围数据的关联
$( "#search_range_select_combine select:first" ).on('change', function (evt) {
    var destion_range_type = evt.currentTarget.value
    //发送更新范围类型请求
    socket.emit('search_setting_change_range_type',{'range_type':destion_range_type})
    to_selector = $( "#search_range_select_combine select:last" )
    // 移除所有option
    to_selector.children().remove()
    // 逐一插入新option
    if(destion_range_type === '公众号'){
        //更新可增加元素
        var availables = search_setting_data['search_range']['gzh_available']
        for(available in availables){
            to_selector.append(new Option(availables[available]))
        }
        //更新已存在元素
        var members = search_setting_data['search_range']['gzh_members']
        $("#search_range_elements").find('span').remove()
        for (member in members){
            var new_element = '<span class="element-tag w3-tag w3-orange w3-text-white w3-round-large" style="padding: 2px;margin: 2px">'+members[member]+'</span>'
            $("#search_range_elements").append(new_element)
        }
    }
    else if(destion_range_type === '类别'){
        //更新可用元素
        var availables = search_setting_data['search_range']['cat_available']
        for(available in availables){
            to_selector.append(new Option(availables[available]))
        }
        // 更新已存在元素
        var members = search_setting_data['search_range']['cat_members']
        $("#search_range_elements").find('span').remove()
        for (member in members){
            var new_element = '<span class="element-tag w3-tag w3-orange w3-text-white w3-round-large" style="padding: 2px;margin: 2px">'+members[member]+'</span>'
            $("#search_range_elements").append(new_element)
        }
    }
})

//从列表中增加搜索范围中的元素
$( "#search_range_select_combine select:last" ).on('change', function (evt) {
    var element_name = evt.target.value
    var range_type = search_setting_data.search_range.current_search_range
    socket.emit('search_setting_add_to_search_range',{'range_type':range_type,'element_name':element_name})
})

// 删除搜索范围中的元素
$("#search_range_elements").on('dblclick', function (evt) {
    var range_type = $( "#search_range_select_combine select:first" )[0].value
    var element_name = evt.originalEvent.target.innerText
    console.log(range_type, element_name)
    socket.emit('search_setting_delete_from_search_range',{'range_type':range_type,'element_name':element_name})
})
// 根据搜索设置数据更新
function refresh__setting_data(setting_data) {
    //更新正在使用搜索类别
    var range_type = search_setting_data.search_range.current_search_range
    $('#search_range_select_combine select:first').val(range_type)
    //更新可添加元素
    var to_selector = $('#search_range_select_combine select:last')
    to_selector.children().remove()
    // 逐一插入新option
    var trans_data = {
        '公众号':'gzh',
        '类别':'cat',
    }
    //更新可增加元素
    var availables = search_setting_data['search_range'][trans_data[range_type]+'_available']
    // 为了避免最后一个元素选择不上
    to_selector.append(new Option('点击选择新增项'))
    for(available in availables){
        to_selector.append(new Option(availables[available]))
    }
    //更新已存在元素
    var members = search_setting_data['search_range'][trans_data[range_type]+'_members']
    $("#search_range_elements").find('span').remove()
    for (member in members){
        var new_element = '<span title="双击标签移除" class="element-tag w3-tag w3-orange w3-text-white w3-round-large" style="padding: 2px;margin: 2px">'+members[member]+'</span>'
        $("#search_range_elements").append(new_element)
    }
}

// 绑定设置数据和socketio事件
socket.on('search_setting', function(data) {
    search_setting_data = data
    refresh__setting_data()
});

// 初始化设置数据
$(document).ready(function () {
    refresh__setting_data()
})