from django.shortcuts import render, redirect
from django.views import View 
from django.views.generic.base import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .models import CustomUser

# Register > TemplateView 
class UserRegister(TemplateView):
    """
    TemplateView의 특징 
    get()는 생략 가능하다. -> 즉, 코딩 안해도 자동 생성됨 
    """
    template_name = "user/register.html"

    def post(self, request):
        try:
            
            username = request.POST.get("username").strip()
            password = request.POST.get("password").strip()
            email = request.POST.get("email").strip()

            CustomUser.objects.create_user(
                name=username, password=password, email=email
            )
            return redirect("user-login")
        except Exception as e:
            messages.error(request, str(e))
            return redirect("user-register")

# Login & Logout > View
class UserLogin(View):
    def get(self, request):
        return render(
            request, "user/login.html"
        ) 

    def post(self, request):
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()

        if not CustomUser.objects.filter(name=username).exists():
            messages.error(request, f"{username}은 존재하지 않는 사용자입니다.")
            return redirect("user-login")

        is_user = authenticate(username=username, password=password)
        if not is_user:
            messages.error(request, f"비밀번호가 올바르지 않습니다.")
            return redirect("user-login")

        login(request, is_user) 
        return redirect("todolist")

class UserLogout(View):
    def get(self, request):
        logout(request)
        return redirect("user-login") 
