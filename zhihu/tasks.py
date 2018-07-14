from celery import shared_task, task
from django_redis import get_redis_connection
from .models import UserMessageCounter, RK_NOTIFICATIONS_COUNTER
from django.db.models import F


@shared_task
def update_counter():
    con = get_redis_connection('default')
    temp = []
    for user_id in con.zrange(RK_NOTIFICATIONS_COUNTER, 0, -1):  #取出所有数据
        pipe = con.pipeline()
        pipe.zscore(RK_NOTIFICATIONS_COUNTER, user_id)
        pipe.zrem(RK_NOTIFICATIONS_COUNTER, user_id)
        count, _ = pipe.execute()
        count = int(count)

        print('Updating unread count user {0}: count {1}'.format(user_id, count))
        #UserMessageCounter.objects.filter(pk=user_id).update(unread_count=F('unread_count') + count)
        # 兼容已存在用户
        user = UserMessageCounter.objects.filter(pk=user_id)
        if user:
            user.update(unread_count=F('unread_count') + count)
        else:
            user = UserMessageCounter.objects.create(pk=user_id)
            user.update(unread_count=F('unread_count') + count)
        temp.append((user_id, count))
    return temp

@shared_task
def xsum(numbers):
    return sum(numbers)


@task               #(name='zhihu.tasks.test')    #appname为当前app注册的名字
def test():
    print ("test")