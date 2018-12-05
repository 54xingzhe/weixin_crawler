from threading import Thread
import time


def frank(config,tasks):
    print(config)
    for t in tasks:
        print(t)
        time.sleep(1)
    return


class MultiTask():
    def __init__(self, worker, tasks, worker_num,config):
        self.worker = worker
        self.tasks = tasks
        self.worker_num = worker_num
        tasks_num = len(tasks)
        if worker_num > tasks_num:
            self.worker_num = tasks_num
            worker_num = tasks_num
        self.worker_tasks = []
        self.config = config
        if tasks_num%worker_num == 0:
            num = tasks_num/worker_num
            for i in range(worker_num):
                b = int(i*num)
                e = int((i+1)*num)
                self.worker_tasks.append(self.tasks[b:e])
        else:
            num = int(tasks_num/worker_num)
            for i in range(worker_num-1):
                b = int(i*num)
                e = int((i+1)*num)
                self.worker_tasks.append(tasks[b:e])
            self.worker_tasks.append(tasks[int((worker_num-1)*num):])

    def run(self):
        self.threads = []
        # 创建任务
        for i in range(self.worker_num):
            self.threads.append(Thread(target=self.worker, args=(self.config,self.worker_tasks[i])))
        # 启动任务
        for i in range(self.worker_num):
            self.threads[i].start()
        # 等待任务结束
        for i in range(self.worker_num):
            self.threads[i].join()
