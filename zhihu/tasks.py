from celery import Celery

app = Celery('tasks',
             broker='redis://192.168.200.127:6379/0',
             backend='redis://192.168.200.127:6379/0')


@app.task
def add(x, y):
    print("running...", x, y)
    return x + y