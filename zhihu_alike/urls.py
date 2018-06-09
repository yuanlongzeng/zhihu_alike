"""zhihu_alike URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve

from rest_framework.routers import DefaultRouter

from zhihu.views import Index,Login,Logout,AnswerListViewSet,QuestionListViewSet,CommentViewSet,TopicViewSet
from zhihu import genericview
import xadmin
router = DefaultRouter()
router.register(r'answer', AnswerListViewSet) #, base_name="answer"
router.register(r'question', QuestionListViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'topic', TopicViewSet)
urlpatterns = [
   # url(r'^admin/', admin.site.urls),

    #第三方工具
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^captcha/', include('captcha.urls')),

    #自定义视图
    url(r'^$',Index.as_view(),name="index"),
    url(r'^login/$',Login.as_view(),name="login"),
    url(r'^logout/$',Logout.as_view(),name="logout"),

    url(r'^userdetail/(?P<pk>.*)$',genericview.IndexView.as_view(),name='user_detail'),
    url(r'^explore/$',genericview.IndexView.as_view(),name='explore'),

    #answer
    url(r'^answercontent/(?P<pk>.*)$',genericview.ShowAnswerView.as_view(),name='answer_content'),
    url(r'^answervoteup/(?P<pk>.*)$',genericview.vote_up,name='answer_voteup'),
    url(r'^answervotedown/(?P<pk>.*)$',genericview.vote_down,name='answer_votedown'),
    url(r'^answerdelete/(?P<pk>.*)$',genericview.DeleteAnswerView.as_view(),name='answer_delete'),
    # question  注意放的顺序：先长后短
    url(r'^question/(?P<pk>.*)/createanswer$', genericview.CreateAnswerView.as_view(), name='question_create'),
    url(r'^question/(?P<pk>.*)/answer/(?P<answer_id>.*)$', genericview.QuestionAnswerDetailView.as_view(), name='question_answer_detail'),
    url(r'^question/(?P<pk>.*)/', genericview.QuestionDetailView.as_view(), name='question_detail'),



    #收藏
    url(r'^answercollect/(?P<pk>.*)$',genericview.collect,name='answer_collect'),
    url(r'^answeruncollect/(?P<pk>.*)$',genericview.uncollect,name='answer_uncollect'),

    # topic
    url(r'^topicdetail/(?P<pk>.*)$', genericview.ShowAnswerView.as_view(), name='topic_detail'),

    #comment
    url(r'^commentslist/(?P<pk>.*)$',genericview.CommentsListView.as_view(),name='comments_list'),
    url(r'^commentsdelete/(?P<pk>.*)$',genericview.DeleteCommentView.as_view(),name='comments_delete'),
    url(r'^commentscreate/(?P<pk>.*)$',genericview.CommentCreateView.as_view(),name='comments_create'),

    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  # 静态文件加载，media文件

    #api
    url(r'^', include(router.urls)),


]
