//监听按键点击事件 通过jquery的选择器获取form的字段
// 添加爬虫
$(document).on('click', 'button.phone_crawler_add_btn', function(evt){
    // 禁止离开当前页面
    evt.preventDefault();
    var button = $(evt.target);
    var result = $('#phone_crawler_add_form').serialize() + '&button=' + encodeURI(button.attr('value'));
    //解码数据
    result = decodeURIComponent(result,true)
    socket.emit('phone_crawler_add', result);
    console.log(result)
});
// 删除爬虫
$(document).on('dblclick', 'button.phone_crawler_delete', function(evt){
    // 禁止离开当前页面
    evt.preventDefault();
    var phone = evt.originalEvent.path[1].childNodes[2].innerText
    phone = phone.replace(' ','')
    socket.emit('phone_crawler_delete', {'phone':phone});
    console.log(phone)
});

// 增加公众号
$(document).on('click', 'button#add_gzh_btn', function(evt){
    // 禁止离开当前页面
    evt.preventDefault();
    var button = $(evt.target);
    var result = $('#add_gzh_from').serialize() + '&button=' + encodeURI(button.attr('value'));
    //解码数据
    result = decodeURIComponent(result,true)
    socket.emit('gzhs_todolist_add', result);
    console.log("增加公众号")
});

//相应表格中点击导出为Excel按钮
$(document).on('click', 'td.export-excel-btn', function(evt){
    $('#excel_nickname').val(this.dataset.nickname)
    $('#excel_option').show()
});

//相应确认生成Excel
$(document).on('click', 'button#gen_excel_btn', function(evt){
    $('#excel_option').hide()
    var result = $('#gen_excel_data').serialize();
    //解码数据
    result = decodeURIComponent(result,true)
    $.post('http://localhost:5000/export_excel', result)
});

// 添加公众号类别 add_gzh_category
$( "#add-gzh-category-btn" ).keyup(function(event) {
    if (event.keyCode === 13) {
        var cat_name = $('#add-gzh-category-btn').val();
        socket.emit('add_gzh_category', cat_name);
    }
});

// 删除公众号类别 delete_gzh_category
$(document).on('dblclick', '.delete-gzh-category-btn', function(evt){
    cat_name = event.path[2].innerText
    socket.emit('delete_gzh_category', cat_name);
});


// 类别添加公众号 add_gzh_to_category
$(document).on('change', '.gzh_tag_add', function(evt){
    nickname = this.value
    cat_name_raw = evt.currentTarget.innerHTML
    socket.emit('add_gzh_to_category', {'cat_name_raw':cat_name_raw,'nickname':nickname});

})

// 类别删除公众号 delete_gzh_from_category
$(document).on('dblclick', '.gzh_tag_remove', function(evt){
    nickname = event.path[0].innerText
    cat_name = event.path[2].innerText.split('\n')[0]
    console.log(nickname, cat_name)
    socket.emit('delete_gzh_from_category', {'cat_name':cat_name,'nickname':nickname});

})

