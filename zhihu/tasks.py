import time

from celery import Celery, shared_task

app = Celery('tasks',
             broker='redis://192.168.200.127:6379/0',
             backend='redis://192.168.200.127:6379/0')


@app.task
def add(x, y):
    print("running...", x, y)
    time.sleep(1)
    return x + y

@shared_task
def xsum(numbers):
    return sum(numbers)