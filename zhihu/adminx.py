import xadmin

from .models import Question,Answer,Message,Comment,Topic,Article,Column
# 创建admin的管理类,这里不再是继承admin，而是继承object
class QuestionAdmin(object):
    # 配置后台我们需要显示的列
    list_display = ['creator', 'title','topics', 'content','clicks', 'created_date','recent_modify_date', 'comment','status']
    # 配置搜索字段,不做时间搜索
    search_fields = ['creator', 'title','topics', 'content','clicks', 'created_date','recent_modify_date', 'comment','status']
    # 配置筛选字段
    list_filter = ['creator', 'title','topics', 'content','clicks', 'created_date','recent_modify_date', 'comment','status']

# 创建回答的管理类
class AnswerAdmin(object):
    list_display = ['user', 'content','created_date', 'recent_modify_date', 'votesup', 'unvotes','question', 'status']
    search_fields = ['user', 'content','created_date', 'recent_modify_date', 'votesup', 'unvotes','question', 'status']
    list_filter = ['user', 'content', 'created_date', 'recent_modify_date', 'votesup', 'unvotes','question', 'status']

class MessageAdmin(object):
    list_display = ['fromid', 'toid', 'content','created_date', 'status']
    search_fields = ['fromid', 'toid', 'content','created_date', 'status']
    list_filter = ['fromid', 'toid', 'content','created_date', 'status']

class CommentAdmin(object):
    list_display = ['user', 'toid', 'content','content_type', 'object_id','created_date', 'status',"reply_to"]
    search_fields = ['user', 'toid', 'content','content_type', 'object_id','created_date', 'status',"reply_to"]
    list_filter = ['user', 'toid', 'content','content_type', 'object_id','created_date', 'status',"reply_to"]


class TopicAdmin(object):
    list_display = ['name', 'desc', 'parent','created_date', 'status',]
    search_fields = ['name', 'desc', 'parent','created_date', 'status',]
    list_filter = ['name', 'desc', 'parent','created_date', 'status',]


class ArticleAdmin(object):
    list_display = ['user', 'title', 'content','column','created_date', 'recent_modify_date', 'status']
    search_fields = ['user', 'title', 'content','column','created_date', 'recent_modify_date', 'status']
    list_filter = ['user', 'title', 'content','column','created_date', 'recent_modify_date', 'status']

class ColumnAdmin(object):
    list_display = ['user', 'name', 'desc','created_date', 'recent_modify_date', 'status']
    search_fields = ['user', 'name', 'desc','created_date', 'recent_modify_date', 'status']
    list_filter = ['user', 'name', 'desc','created_date', 'recent_modify_date', 'status']

# 将model与admin管理器进行关联注册
xadmin.site.register(Question, QuestionAdmin)
xadmin.site.register(Answer, AnswerAdmin)

xadmin.site.register(Message, MessageAdmin)
xadmin.site.register(Comment, CommentAdmin)

xadmin.site.register(Topic, TopicAdmin)

xadmin.site.register(Article, ArticleAdmin)
xadmin.site.register(Column, ColumnAdmin)