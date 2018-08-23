import unittest
import os

from django.core.management.base import BaseCommand
import coverage

from zhihu_alike.settings import BASE_DIR
omit_dir = ['tests/*',
        'zhihu_alike/*',
        'extra_apps/']
COV = coverage.coverage(
    branch=True,
    include= BASE_DIR,
    omit=[
        os.path.join(BASE_DIR,dir) for dir in omit_dir
    ]
)
COV.start()

class Command(BaseCommand):
    '''
    检测测试用例的覆盖范围
    '''
    help = 'Code coverage is the process of finding areas of your code not covered by tests'

    def handle(self, *args, **options):
        tests = unittest.TestLoader().discover(os.path.join(BASE_DIR,'tests'))
        result = unittest.TextTestRunner(verbosity=2).run(tests)
        if result.wasSuccessful():
            COV.stop()
            COV.save()
            print('Coverage Summary:')
            COV.report()
            COV.html_report()
            COV.erase()
            return 0
        return 1