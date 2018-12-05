from ui import run_webserver
from ui import run_gzh_crawler

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_webserver, args=()).start()
    run_gzh_crawler()
