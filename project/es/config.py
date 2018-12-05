# 需要在es中进行index 文档字段
doc_schema = {
    # "nickname":     {"type":"text","analyzer": "ik_max_word","search_analyzer": "ik_max_word"},
    "title":        {"type":"text","analyzer": "ik_max_word","search_analyzer": "ik_max_word"},
    # "article_id":   {"type":"integer"},
    "content_url":  {"type":"text"},
    "source_url":   {"type":"text"},
    "digest":       {"type":"text","analyzer": "ik_max_word","search_analyzer": "ik_max_word"},
    "cover":        {"type":"text"},
    "p_date":       {"type":"date"},
    # "with_ad":      {"type":"boolean"},
    "pic_num":      {"type":"integer"},
    "video_num":    {"type":"integer"},
    # "read_num":     {"type":"integer"},
    # "like_num":     {"type":"integer"},
    # "comment_id":   {"type":"text"},
    # "comment_num":  {"type":"integer"},
    # "comments":     {"type":"object"},
    # "reward_num":   {"type":"integer"},
    "author":       {"type":"text","analyzer": "ik_max_word","search_analyzer": "ik_max_word"},
    "mov":          {"type":"short"},
    # "title_emotion":{"type":"text","analyzer": "ik_max_word","search_analyzer": "ik_max_word"},
    # "title_token":  {"type":"nested"},
    # "title_token_len":{"type":"integer"},
    # "human_digest_token":{"type":"nested"},
    "article":      {"type":"text","analyzer": "ik_max_word","search_analyzer": "ik_max_word"},
    # "article_token":{"type":"nested"},
    # "article_token_len":{"type":"integer"},
    # "c_date":       {"type":"date"}
}


# 搜索body模板
search_template = {
    "query":{"match_all":{}},
    "from":0,
    "size":20,
    "sort":[],
    "highlight" : {
        "pre_tags" : ["<span style='color:#dd4b39'>"],
        "post_tags" : ["</span>"],
        "fields" : {
            "nickname":{},
            "title":{},
            "digest":{},
            "author":{},
            "title_emotion":{},
            "article":{}
        }
    }
}
