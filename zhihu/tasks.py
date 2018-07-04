import time

from celery import Celery, shared_task, task
import celery
# app = Celery('tasks',
#              broker='redis://192.168.200.127:6379/0',
#              backend='redis://192.168.200.127:6379/0')
#
#
# @app.task
# def add(x, y):
#     print("running...", x, y)
#     time.sleep(1)
#     return x + y

@shared_task
def xsum(numbers):
    return sum(numbers)


@celery.task               #(name='zhihu.tasks.test')    #appname为当前app注册的名字
def test():
    print ("test")