//累计发文总数
document.getElementById('total_posts_num').innerHTML = '{{ data.account_name }}累计发文'+{{ data.total_posts_num }}


// 历史主文章的发布时间/阅读量/点赞量/赞赏量/评论量
echarts.init(document.getElementById('all_mian_date_read')).setOption({{ data.all_mian_date_read }})

// 主副文章统计数据
echarts.init(document.getElementById('all_statistic')).setOption({{ data.all_statistic }})

// 分别统计不同主副/小时/星期文章发文数量
echarts.init(document.getElementById('dir_posts_num_related_mov')).setOption({{ data.dir_posts_num_related.mov }})
echarts.init(document.getElementById('dir_posts_num_related_hour')).setOption({{ data.dir_posts_num_related.hour }})
echarts.init(document.getElementById('dir_posts_num_related_week')).setOption({{ data.dir_posts_num_related.week }})

//阅读量分别和点赞量/上一次阅读量之间的关系
echarts.init(document.getElementById('read_vs_like')).setOption({{ data.read_vs_factors.like }})
echarts.init(document.getElementById('read_vs_pre_read')).setOption({{ data.read_vs_factors.pre_read }})
echarts.init(document.getElementById('read_vs_article_token')).setOption({{ data.read_vs_factors.article }})

// 探索最佳推文小时 推文星期 标题词数 插图数量 视频数量
echarts.init(document.getElementById('read_vs_hour')).setOption({{ data.find_best_factors.hour }})
echarts.init(document.getElementById('read_vs_week')).setOption({{ data.find_best_factors.week }})
echarts.init(document.getElementById('read_vs_title')).setOption({{ data.find_best_factors.title }})
echarts.init(document.getElementById('read_vs_pic')).setOption({{ data.find_best_factors.pic }})
echarts.init(document.getElementById('read_vs_video')).setOption({{ data.find_best_factors.video }})


{% macro table_list(table_data) -%}
`
<table class="w3-table w3-striped w3-white">
    <thead>
        <tr>
            <th scope="col">序号</th>
            <th scope="col">阅读量</th>
            <th scope="col">点赞量</th>
            <th scope="col">标题</th>
            <th scope="col">发文日期</th>
            <th scope="col">{{ table_data.attribute }}</th>
        </tr>
    </thead>
    <tbody>
        {% for data in table_data.data %}
        <tr>
            <td>{{ data.id }}</td>
            <td>{{ data.read }}</td>
            <td>{{ data.like }}</td>
            <td><a class='text-body' href={{ data.url }} target="_blank">{{ data.title_cnt }}</a></td>
            <td>{{ data.date }}</td>
            <td>{{ data.attribute }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
`
{%- endmacro %}
// 表9 100001除外阅读来那个最高的10篇文章
document.getElementById('particular_most_read_10_except_100001').innerHTML = {{ table_list(data.table.particular_most_read_10_except_100001) }}
// 表10 阅读量最低且为非0的10篇文章
document.getElementById('particular_least_read_10_except_0').innerHTML = {{ table_list(data.table.particular_least_read_10_except_0) }}
// 表11 深度指数最高的10篇文章
document.getElementById('particular_most_deep_10').innerHTML = {{ table_list(data.table.particular_most_deep_10) }}
// 表12 深度指数最低的10篇文章
document.getElementById('particular_least_deep_10').innerHTML = {{ table_list(data.table.particular_least_deep_10) }}
// 表13 容易指数最高的10篇文章
document.getElementById('particular_most_easy_10').innerHTML = {{ table_list(data.table.particular_most_easy_10) }}
// 表14 容易指数最低的10篇文章
document.getElementById('particular_least_easy_10').innerHTML = {{ table_list(data.table.particular_least_easy_10) }}
// 表15 落差指数最低的10篇文章
document.getElementById('particular_least_fall_10').innerHTML = {{ table_list(data.table.particular_least_fall_10) }}
// 表16 所有的100001文章
document.getElementById('particular_all_10001').innerHTML = {{ table_list(data.table.particular_all_10001) }}


// {# echarts.init(document.getElementById(' ')).setOption({{ data.. }}) #}
// 标题/摘要/正文/评论/回复词云(词频)
var word_cloud_title = echarts.init(document.getElementById('word_cloud_title'));
word_cloud_title.setOption({{ data.word_cloud.wc_title }})

var word_cloud_digest = echarts.init(document.getElementById('word_cloud_digest'));
word_cloud_digest.setOption({{ data.word_cloud.wc_digest }})

var word_cloud_article = echarts.init(document.getElementById('word_cloud_article'));
word_cloud_article.setOption({{ data.word_cloud.wc_article }})

var word_cloud_comment = echarts.init(document.getElementById('word_cloud_comment'));
word_cloud_comment.setOption({{ data.word_cloud.wc_comment }})

var word_cloud_reply = echarts.init(document.getElementById('word_cloud_reply'));
word_cloud_reply.setOption({{ data.word_cloud.wc_reply }})
