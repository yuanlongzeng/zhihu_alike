from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View


class Index(View):
    def get(self,request):
        return render(request,"index.html",context={})

class Login(View):
    def get(self,request):
        return render(request,"login.html",context={})