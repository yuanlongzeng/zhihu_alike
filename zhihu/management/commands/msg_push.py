import json

from django.core.management import BaseCommand
from django.conf import settings
import redis

from zhihu.consumers import ChatConsumer

class Command(BaseCommand):
    """
    Command to start zabbix alert worker from command line.
    """
    help = 'Subscribe the zabbix alerts channel'
    def handle(self, *args, **options):
        rc = redis.Redis(host=settings.REDIS_OPTIONS['HOST'],
                         password=settings.REDIS_OPTIONS['PASSWD'],
                         port=settings.REDIS_OPTIONS['PORT'],
                         db=settings.REDIS_OPTIONS['DB'])
        rc.delete(settings.GROUP_NAME)
        pubsub = rc.pubsub()
        pubsub.subscribe(settings.GROUP_NAME)
        for item in pubsub.listen():
            if item['type'] == 'message':
                #Group(settings.GROUP_NAME).send({'text': bytes.decode(item['data'])})
                ChatConsumer().receive({'message': bytes.decode(item['data']),'status':'normal'})
