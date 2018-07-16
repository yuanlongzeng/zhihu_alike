from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic.base import View

from rest_framework.response import Response
from rest_framework import mixins, status
from rest_framework import generics
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from zhihu.models import UserProfile, Comment, Topic, Message, update_unread_count
from .forms import LoginForm, RegisterForm


class Index(View):
    def get(self,request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse("explore"))
            #return HttpResponseRedirect(reverse("login"))
        #取用户的关注列表、话题等 然后根据用户活跃度使用推还是拉模式
        #还得有分页设置--最好使用drf来完成

        data = {"username":"xx","type":"热门回答","comment_num":99,"topic":"电动力学",'desc':"too science","content":"电动力学的推荐书是两本：1、Griffiths《Introduction to Electrodynamics》。Griffiths的教材都很经典，这本也不例外。讲得很清楚，也很容易入手。不过国内的学生读起来可能会感觉过于简单，其实大部分内容很接近一般普物电磁学教材的难度，但是数学更严格"}
        return render(request,"index.html",context={"request":request,"data":data})

class IndexViewset(viewsets.ModelViewSet):
    pass

#自定义用户登录验证
class CustomAuth(ModelBackend):  # 自定义用户登录验证查询
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(mobile=username) | Q(email=username)| Q(username=username)| Q(nick_name=username))  # 未查到或者查找到多个都会抛出异常
            if user.check_password(password):
                return user
        except:
            return None
class Login(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return render(request,"login.html",context={})
        return HttpResponseRedirect(reverse("index"))

    def post(self,request):
        login_form= LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("account", "")
            pass_word = request.POST.get("password", "")
            # 成功返回user对象,失败返回null
            user = authenticate(username=user_name, password=pass_word)

            data = dict()
            if user is not None:
                if user.status == True:
                    login(request, user)
                    data['ok'] = True
                else:
                    data['ok'] = False
                    data['message'] = '用户未激活'
            else:
                data['ok'] = False
                data['message'] = '用户名或密码错误'
            return JsonResponse(data, status=200)
        else:
            return render(request, "login.html", {"login_form": login_form})

class Logout(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class RegisterView(View):

    def post(self,request):
        data = dict()
        form = RegisterForm(request.POST)
        if form.is_valid():
            #user = form.save()
            user = UserProfile()
            user.username = request.POST.get("username","")
            user.nick_name = request.POST.get("nick_name", "")
            user.email = request.POST.get("email","")

            user.mobile = user.email

            user.status = False  # 未激活 #和is_active重复了

            # 加密password进行保存
            password = request.POST.get("password1")
            user.password = make_password(password)
            user.save()
            login(request, user)
            #logger.info('register: {}'.format(user))
            data['ok'] = True
        else:
            data['ok'] = False
            data['errors'] = form.errors
        return JsonResponse(data, status=200)
    def get(self,request):
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
############3DRF################

#所有用户可以看到的，未登录时也是跳转到这
from .models import Answer,Question
from .serializer import AnswerSerializer, QuestionSerializer, QuestionCreateSerializer, AnswerCreateSerializer, \
    CommentSerializer, TopicSerializer


class AnswerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


class AnswerListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin, mixins.DestroyModelMixin,viewsets.GenericViewSet):
    """
    Answer列表页
    """
    # throttle_classes = (UserRateThrottle, )
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    pagination_class = AnswerPagination
    #authentication_classes = (TokenAuthentication, )
    #filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    #filter_class = AnswerFilter
    #search_fields = ('name', 'goods_brief', 'goods_desc')
    #ordering_fields = ('sold_num', 'shop_price')
    #不做额外的操作就不必重写该函数
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     # instance.click_num += 1
    #     # instance.save()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

    def get_serializer_class(self):
        '''
        不能共用一个序列化类，depth，信息也要一块传递
        :return:
        '''
        if self.action == "retrieve":
            return AnswerSerializer
        elif self.action == "create":
            return AnswerCreateSerializer

        return AnswerSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        #不真正删除
        instance.status = False
        instance.save()

class QuestionPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


class QuestionListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin, mixins.DestroyModelMixin,viewsets.GenericViewSet):
    """
    Answer列表页
    """
    # throttle_classes = (UserRateThrottle, )
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    pagination_class = QuestionPagination
    #authentication_classes = (TokenAuthentication, )
    #filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    #filter_class = AnswerFilter
    #search_fields = ('name', 'goods_brief', 'goods_desc')
    #ordering_fields = ('sold_num', 'shop_price')
    def get_serializer_class(self):
        '''
        不能共用一个序列化类，depth，信息也要一块传递
        :return:
        '''
        if self.action == "retrieve":
            return QuestionSerializer
        elif self.action == "create":
            return QuestionCreateSerializer

        return QuestionSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        #不真正删除
        instance.status = False
        instance.save()

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         # instance.click_num += 1
#         # instance.save()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)
#
#     def create(self, request, *args, **kwargs):
#         '''
#         {
# "creator":1,
# "editor":1,
# "title": "你的问题？",
#     "content": "具体要问什么",
#     "clicks": 0,
#     "created_date": "2018-05-29T20:57:44.120890+08:00",
#     "recent_modify_date": "2018-05-29T20:57:44.120890+08:00",
#     "status": true,
#     "topics":[1,2]
# }
#         '''
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         #保存数据
#         user = self.perform_create(serializer)
#
#         re_dict = serializer.data
#         # payload = jwt_payload_handler(user)
#         # re_dict["token"] = jwt_encode_handler(payload)
#         #re_dict["name"] = user.name if user.name else user.username
#
#         headers = self.get_success_headers(serializer.data)
#         return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)
#
#     def get_object(self):
#         return self.request.user
#
#     def perform_create(self, serializer):
#         return serializer.save()


class CommentViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = QuestionPagination #可以共用--写在配置文件中

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        #不真正删除
        instance.status = False
        instance.save()

class TopicViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    pagination_class = QuestionPagination #可以共用--写在配置文件中

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        #不真正删除
        instance.status = False
        instance.save()


def usertest(request):
    data = {"userid":1}
    return render(request,"usertest.html",context=data)

class userfloatbox(View):
    def get(self,request):
        followed = False
        userid = request.GET.get('userid',1)
        user = UserProfile.objects.get(id=int(userid))
        if request.user.is_authenticated:
            if request.user.is_following(user):
                followed = True
        return render(request,"userfloatbox.html",{"user":user,"followed":followed})


MESSAGE_TIMEOUT = 10


def clean_thanksmessages(zhihuuser, messages):
    u_messages = {}
    t_messages = {}
    for item in messages:
        question_id = item.msg_question.id
        question_url = item.msg_question.get_absolute_url()
        question_title = item.msg_question.title
        user_name = item.from_user.nick_name
        user_url = item.from_user.id
        msg_type = item.msg_type
        has_read = item.has_read
        data = (question_url, user_name, user_url, msg_type, has_read, question_title)
        if msg_type == 'U':
            if u_messages in question_id:
                u_messages[question_id].append(data)
            else:
                u_messages[question_id] = [data, ]
        elif msg_type == 'T':
            if t_messages in question_id:
                t_messages[question_id].append(data)
            else:
                t_messages[question_id] = [data, ]

#更新未读消息数量
def mark_as_read(user,notificationType=None):
    rows = 0
    if notificationType == None:
        print ('MARK ALL: ', user)
        rows = Message.objects.filter(to_user=user,has_read=False).update(has_read=True)
    else:
        raw = Message.objects.filter(to_user=user,has_read=False)
        if notificationType == 'user':
            rows = raw.filter( Q(msg_type='F') ).update(has_read=True)
        elif notificationType == 'thanks':
            rows = raw.filter( Q(msg_type='U') | Q(msg_type='T') ).update(has_read=True)
        elif notificationType == 'common':
            rows = raw.filter( Q(msg_type='RF') | Q(msg_type='RQ') \
                            | Q(msg_type='CF') | Q(msg_type='IF') ).update(has_read=True)
    update_unread_count(user.id, 0-rows)  #清除未读消息数量


def clean_commonMessages(user,raw_messages):
    messages = []
    r_messages = {}
    for item in raw_messages:
        question_id = item.msg_question.id
        question_title = item.msg_question.title
        question_url = item.msg_question.id
        user_name = item.from_user.nick_name
        user_url = item.from_user.id
        msg_type = item.msg_type
        has_read = item.has_read
        if msg_type == 'CF' or msg_type == 'IF':
            messages.append({'question_id':question_id,'question_url':question_url,
                             'user_name':user_name,'user_url':user_url,
                             'msg_type':msg_type,'has_read':has_read, 'question_title':question_title})
        elif msg_type == 'RF' or msg_type == 'RQ':
            data = {'question_id':question_id,'question_url':question_url,
                    'user_name':user_name,'user_url':user_url,
                    'msg_type':'R','has_read':has_read, 'question_title':question_title}
            if r_messages in question_id:
                r_messages[question_id].append( data )
            else:
                r_messages[question_id] = [data,]

    def user_merge(users):
        merged = {}
        for user in users:
            merged[user['user_name']] = user['user_url']
        merged_users = []
        for user in merged:
            merged_users.append({'user_name':user,'user_url':merged[user]})
        return merged_users

    for question_id in r_messages:
        data = {'question_id':question_id,'question_url':r_messages[question_id][0]['question_url'],
                'users':[],
                'msg_type':r_messages[question_id][0]['msg_type'],'has_read':r_messages[question_id][0]['has_read'],
                'question_title':r_messages[question_id][0]['question_title']}
        for item in r_messages[question_id]:
            data['users'].append({'user_name':item['user_name'],'user_url':item['user_url']})
        data['users'] = user_merge(data['users'])
        messages.append(data)
    return messages


#@login_required   http://127.0.0.1:8000/accounts/login/?next=/msglist/%3FmessageType%3Duser  ???????????  @login_required与LoginRequiredMixin处理方式的异同
class MsgListView(LoginRequiredMixin,View):
    messageType = None
    def get(self,request):
        messageType = request.GET['messageType']
        args = dict()
        zhihuuser = request.user  #.zhihuuser  ？
        notifies = Message.objects.filter(~Q(from_user__id=zhihuuser.id)) \
            .filter(to_user__id=zhihuuser.id)

        if messageType == 'thanks':
            if cache.get('thanksmessage') == None:
                messages = notifies.filter(Q(msg_type='U') | Q(msg_type='T'))
                args['messages'] = clean_thanksmessages(zhihuuser, messages)
                #                 args['messages'] = messages
                response = render(request, 'message_thanks.html', args)
                cache.set('thanksmessage', response, MESSAGE_TIMEOUT)
                mark_as_read(zhihuuser, 'thanks')
            else:
                pass
            return cache.get('thanksmessage')
        elif messageType == 'user':
            if cache.get('usermessage') == None:
                messages = notifies.filter(Q(msg_type='F')) #关注
                args['messages'] = messages
                response = render(request, 'message_user.html', args)
                cache.set('usermessage', response, MESSAGE_TIMEOUT)
                mark_as_read(zhihuuser, 'user')
            else:
                pass
            return cache.get('usermessage')
        elif messageType == 'common':
            if cache.get('commonmessage') == None:

                messages = notifies.filter(Q(msg_type='RF') | Q(msg_type='RQ') \
                                           | Q(msg_type='CF') | Q(msg_type='IF'))
                args['messages'] = clean_commonMessages(zhihuuser, messages)
                #                 args['messages'] = messages
                response = render(request, 'message_common.html', args)
                cache.set('commonmessage', response, MESSAGE_TIMEOUT)
                mark_as_read(zhihuuser, 'common')
            else:
                pass
            return cache.get('commonmessage')


class UserDetailView(View):
    def get(self,request,userid):
        user = UserProfile.objects.get(pk=userid)
        is_follow = False
        if not isinstance(request.user,AnonymousUser):
            is_follow = request.user.is_following(user)
        return render(request,"detail.html",{"people":user,"is_following":is_follow})