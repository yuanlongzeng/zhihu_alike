from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic.base import View

from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from zhihu.models import UserProfile
from .forms import LoginForm



class Index(View):
    def get(self,request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse("login"))
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
            user = UserProfile.objects.get(Q(mobile=username) | Q(email=username))  # 未查到或者查找到多个都会抛出异常
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
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            # 成功返回user对象,失败返回null
            user = authenticate(username=user_name, password=pass_word)

            if user is not None:
                # 实际是对request写了一部分东西进去，然后在render的时候：
                # request是要render回去的。这些信息也就
                login(request, user)
                #应该加个从哪个页面跳转过来的从而好跳转回去
                return HttpResponseRedirect(reverse("index"))
                # return render(request, "users/index.html")
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误,请重试", "login_form": login_form})
        else:
            return render(request, "login.html", {"login_form": login_form})

class Logout(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))



############3DRF################

#所有用户可以看到的，未登录时也是跳转到这
from .models import Answer
from .serializer import AnswerSerializer
class AnswerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


class AnswerListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表页, 分页， 搜索， 过滤， 排序
    """
    # throttle_classes = (UserRateThrottle, )
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    pagination_class = AnswerPagination
    # authentication_classes = (TokenAuthentication, )
    #filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    #filter_class = AnswerFilter
    #search_fields = ('name', 'goods_brief', 'goods_desc')
    #ordering_fields = ('sold_num', 'shop_price')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # instance.click_num += 1
        # instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

