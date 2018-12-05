from crawler.crawler import settings


def get_global_settings():
    """
    :return:从crapy的全局设置脚本settings.py中获取所有的设置文件
    """
    custom_settings = {}
    keys = [item for item in dir(settings) if not item.startswith("__")]
    for key in keys:
        custom_settings[key] = getattr(settings, key)
    return custom_settings


if __name__ == "__main__":
    data = get_global_settings()
    print(data)
