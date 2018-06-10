from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
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

from zhihu.models import UserProfile, Comment, Topic
from .forms import LoginForm



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