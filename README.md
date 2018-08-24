# zhihu_alike
仿知乎

## 说明
本来想使用dajngo-rest-framework完成，但是得学习VUE这样的前端框架，所以就使用了
django的通用视图了，也很方便，参考了[FakeZhihu](https://github.com/chris5641/FakeZhihu "FakeZhihu")

消息系统参考[zhihuCopy](https://github.com/threegirl2014/zhihuCopy 'link')

## 问题
* 时区问题？

## 总结
* 生成本项目的requirements.txt  
`pip install pipreqs`  
`pipreqs --encoding=utf8 ./`

* 使用`xadmin`作为后台管理
* 使用`faker`生成模拟数据，同时了解了`django`的 commands 编写方法
* 了解`django-rest-framework` 生成restful接口
* 复杂表关系：`content type
* `djcelery`执行`celery`任务`
* `jwt`第三方登录，使用`social_django`
* `drf_extensions`增强drf的功能
* 使用`redis`缓存，`django_redis`  了解`rabbitmq` 使用`docker`搭建服务
* `django_debug_toolbar`优化sql查询，学会正确使用 `prefetch_related   select_related`
* `Sentry`  集中式日志管理系统,使用`docker`搭建本地服务
