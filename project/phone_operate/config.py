# OCR 没有识别到任何结果返回参数
OCR_NO_WORDS = []

# Android按键事件
KEY={
    'BACK_KEYEVENT' : '4',
    'HOME_KEYEVENT' : '3',
}

# 微信位置信息
BTN={
    # 微信主界面底部4个按钮
    'WEIXIN_BTN' : (120,1800,200,1900),
    'TONGXUNLU_BTN' : (380,1800,460,1900),
    'FAXIAN_BTN' : (620,1800,700,1900),
    'WO_BTN' : (920,1800,1000,1900),
    # 公众号文件夹列表
    'GZH_FOLDER':(0,640,900,750),
    # 搜索公众号的第一个结果
    'FIRST_GZH_SEARCH_RESULT':(34,225,900,330),
    # 所有关注公众号列表右上角2个按钮
    'SEARCH_BTN' : (800,120,860,200),
    'ADD_BTN' : (950,100,1020,200),
    # 公众号详情按钮
    'PROFILE_BTN' : (950,100,1020,200),
    # 更多按钮
    'MORE_BTN' : (950,100,1020,200),
    'CLAIRE_WEIXIN' : (130,1350,200,1400),
    #每个模拟器统一位置
    'EMU_WEIXIN_ICON':(920,670,1000,750),
    # 根据拼音搜索公众号的第一个结果位置
    'FIRST_RESULT':(200,220,800,350),
    # 证书提示继续钮位置
    'CAR_NOTE_CONTINUE':(780,1200,900,1250),
    # 公众号全部消息按键
    'ALL_HISTORY_MSG':(34,1720,1024,1800),
    # 允许使用地理位置确认按钮
    'ASK_FOR_LOCATION':(780,1150,860,1180),
    # 写了留言按钮
    'LEAVE_MSG':(480,1770,580,1790),
    # 由于标题行数不同确认留言位置也不同 索性点击三次
    'CONFIRM_MSG1':(120,760,940,850),
    'CONFIRM_MSG2':(120,830,940,920),
    'CONFIRM_MSG3':(120,900,940,990),
}

CROP_RANGE = {
    'MESSAGE_LIST':(0,220,700,1920),
    'PROFILE_MESSAGE_LIST':(0,820,700,1680),
    'CAR_NOTE':(130,700,950,1270),
    'LEAVE_MSG_BOTTOM':(0,1650,1080,1920),
}

UI_WORDS = {
    'CAR_NOTE':'该网站的安全证书存在问题',
    'NO_LEAVING_MSG':'写留言',
}

PHONE = {
    'PXX':{'phone':'127.0.0.1:62025','phone_model':'SM-G955A'},
    'DRMJ':{'phone':'127.0.0.1:62001','phone_model':'SM-N950W'},
    'Claire':{'phone':'127.0.0.1:62027','phone_model':'SM-G930K'},
    'Frank':{'phone':'127.0.0.1:62026','phone_model':'SM-N9007'},
    'XZP':{'phone':'127.0.0.1:62028','phone_model':'SM-N9089'},
}

