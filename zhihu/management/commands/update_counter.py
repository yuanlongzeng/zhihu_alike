from django.core.management.base import BaseCommand


from django.db.models import F

from zhihu.models import UserMessageCounter
from zhihu.models import RK_NOTIFICATIONS_COUNTER
from django_redis import get_redis_connection

class Command(BaseCommand):
    '''
    使用manage command 更新  还可以使用celery tasks定时更新
    '''
    help = 'Update UserNotificationsCounter objects, Write changes from redis to database'
    
    def handle(self, *args, **options):
        con = get_redis_connection('default')
        for user_id in con.zrange(RK_NOTIFICATIONS_COUNTER,0,-1):
            pipe = con.pipeline()
            pipe.zscore(RK_NOTIFICATIONS_COUNTER,user_id)
            pipe.zrem(RK_NOTIFICATIONS_COUNTER,user_id)
            count,_ = pipe.execute()
            count = int(count)
            
            self.stdout.write( 'Updating unread count user {0}: count {1}'.format(user_id, count) )
            #UserMessageCounter.objects.filter(pk=user_id).update(unread_count=F('unread_count') + count)
            #兼容已存在用户
            user = UserMessageCounter.objects.filter(pk=user_id)
            if user:
                user.update(unread_count = F('unread_count') + count)
            else:
                user = UserMessageCounter.objects.create(pk=user_id)
                user.update(unread_count=F('unread_count') + count)