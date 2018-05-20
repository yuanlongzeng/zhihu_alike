from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic.base import View

from zhihu.models import UserProfile
from .forms import LoginForm



class Index(View):
    def get(self,request):
        return render(request,"index.html",context={"request":request})
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
        return render(request,"login.html",context={})

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

