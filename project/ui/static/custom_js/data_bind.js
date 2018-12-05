//当前在工作的微信爬虫
var vm_phone_crawler_data = new Vue({
    el: '#vm-app-phone-crawler-data',
    data: {
        crawlers:[{
                "adb_port":'...',       //#adb手机端口
                "nick_name":"...",      //#登陆该手机的微信名称
                "wxuin":'...',          //#微信账号昵称
             }
        ]
    },
});

//显示当前的爬取文章队列
var vm_articles_logger_monitoring = new Vue({
    el: '#vm-app-articles-logger-monitoring',
    data: {
        articles:[
            {
                'nickname':'...',
                'percent':'...',
                'more':'...',
                'title':'...'
            }
        ]
    },
});

//已经完成采集公众号列表数据绑定
var vm_gzhs_list_data = new Vue({
    el:'#vm-app-gzhs-list-data',
    data: {
        gzhs:{
            meta:{'total_gzh':0,'total_article':0},
            data:[
                {
                    nickname:'...',
                    article_num:'...',
                    update_time:'...',
                    update_num:'...',
                }
            ]
        }
    },
});

//正在爬取的公众号列表数据绑定
var vm_gzhs_todolist_data = new Vue({
    el:'#vm-app-gzhs-todolist-data',
    data:{
        gzhs:[
            {
                nickname:'...',
                percent:'...',
                begin_time:'...',
                need_time:'...'
            }
        ]
    }
})

// 公众号分类设置
var vm_app_gzh_category_data = new Vue({
    el:'#vm-app-gzh-category-data',
    data:{
        category : [
            {
                "cat_name":'...',
                "cat_members":['...'],
                "cat_available":['...']
            }
        ]
    }
})
