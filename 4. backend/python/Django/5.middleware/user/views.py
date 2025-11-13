from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib.auth import login, logout
from django.contrib import messages

from .services import insert_user, get_user
 
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

            insert_user(username, password, email)
            return redirect("user-login")
        except Exception as e:
            messages.error(request, str(e))
            return redirect("user-register")

class UserLogin(View):
    def get(self, request):
        return render(
            request, "user/login.html"
        )

    def post(self, request):
        try:
            username = request.POST.get("username").strip()
            password = request.POST.get("password").strip()
            
            user = get_user(username, password)
            login(request, user)
            return redirect("todolist") 
        except Exception as e:
            messages.error(request, str(e))
            return redirect("user-login")

class UserLogout(View):
    def get(self, request):
        logout(request)
        return redirect("user-login")
