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

from zhihu.views import Index,Login,Logout,AnswerListViewSet,QuestionListViewSet,CommentViewSet,TopicViewSet,RegisterView,usertest,userfloatbox
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
    url(r'^index/$',genericview.IndexView.as_view(),name="index"),
    url(r'^login/$',Login.as_view(),name="login"),
    url(r'^logout/$',Logout.as_view(),name="logout"),
    url(r'^register/$',RegisterView.as_view(),name="register"),

    url(r'^usertest/',usertest,name='usertest'),
    url(r'^userfloatbox/',userfloatbox.as_view(),name='userfloatbox'),
    url(r'^userfollow/(?P<userid>.*)$',genericview.FollowUserView.as_view(),name='userfollow'),

    url(r'^userdetail/(?P<pk>.*)$',genericview.IndexView.as_view(),name='user_detail'),
    url(r'^explore/$',genericview.ExploreView.as_view(),name='explore'),

    #answer
    url(r'^answercontent/(?P<pk>.*)$',genericview.ShowAnswerView.as_view(),name='answer_content'),
    url(r'^answervoteup/(?P<pk>.*)$',genericview.vote_up,name='answer_voteup'),
    url(r'^answervotedown/(?P<pk>.*)$',genericview.vote_down,name='answer_votedown'),
    url(r'^answerdelete/(?P<pk>.*)$',genericview.DeleteAnswerView.as_view(),name='answer_delete'),
    # question  注意放的顺序：先长后短
    url(r'^question/(?P<pk>.*)/createanswer$', genericview.CreateAnswerView.as_view(), name='question_create'),
    url(r'^question/(?P<pk>.*)/answer/(?P<answer_id>.*)$', genericview.QuestionAnswerDetailView.as_view(), name='question_answer_detail'),
    url(r'^question/(?P<pk>.*)/', genericview.QuestionDetailView.as_view(), name='question_detail'),
    url(r'^questionfollow/(?P<pk>.*)$',genericview.follow_ask,name='answer_votedown'),
    url(r'^questionunfollow/(?P<pk>.*)$',genericview.unfollow_ask,name='answer_votedown'),



    #收藏
    url(r'^answercollect/(?P<pk>.*)$',genericview.collect,name='answer_collect'),
    url(r'^answeruncollect/(?P<pk>.*)$',genericview.uncollect,name='answer_uncollect'),


    #comment
    url(r'^commentslist/(?P<pk>.*)$',genericview.CommentsListView.as_view(),name='comments_list'),
    url(r'^commentsdelete/(?P<pk>.*)$',genericview.DeleteCommentView.as_view(),name='comments_delete'),
    url(r'^commentscreate/(?P<pk>.*)$',genericview.CommentCreateView.as_view(),name='comments_create'),

    #topics
    url(r'^topics/$',genericview.TopicsView.as_view(),name='topics_list'),
    url(r'^topics/(?P<pk>.*)$',genericview.TopicDetail.as_view(),name='topic_detail'),
    url(r'^topic_follow/(?P<pk>.*)$',genericview.TopicFollowView.as_view(),name='topic_follow'),

    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  # 静态文件加载，media文件
    #第三方登录验证
    url('', include('social_django.urls', namespace='social')),
    #rest api
    url(r'^', include(router.urls)),


]
