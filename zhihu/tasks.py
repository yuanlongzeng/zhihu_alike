from celery import shared_task
from django_redis import get_redis_connection
from .models import UserNotificationCounter, RK_NOTIFICATIONS_COUNTER
from django.db.models import F


@shared_task
def update_counter():
    con = get_redis_connection('default')
    temp = []
    for user_id in con.zrange(RK_NOTIFICATIONS_COUNTER, 0, -1):
        pipe = con.pipeline()
        pipe.zscore(RK_NOTIFICATIONS_COUNTER, user_id)
        pipe.zrem(RK_NOTIFICATIONS_COUNTER, user_id)
        count, _ = pipe.execute()
        count = int(count)

        print('Updating unread count user {0}: count {1}'.format(user_id, count))
        UserNotificationCounter.objects.filter(pk=user_id).update(unread_count=F('unread_count') + count)
        temp.append((user_id, count))
    return temp

@shared_task
def xsum(numbers):
    return sum(numbers)


@celery.task               #(name='zhihu.tasks.test')    #appname为当前app注册的名字
def test():
    print ("test")