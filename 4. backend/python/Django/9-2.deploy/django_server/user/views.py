from django.shortcuts import redirect
from django.views import View 
from django.views.generic.base import TemplateView
from django.contrib.auth import login, logout
from django.contrib import messages

from .services import user_by_valid_login
from .forms import LoginForm, RegisterForm

# 가입 화면 
class UserRegister(TemplateView):
    template_name = "user/register.html"

    def get_context_data(self):
        context = super().get_context_data()
        context['form'] = RegisterForm()
        return context

    def post(self, request):
        try:
            form = RegisterForm(request.POST)
            if form.is_valid():     # 사용자가 입력한 데이터 검증 
                form.save()         # 데이터베이스에 저장 
                return redirect("login")
            
            messages.error(request, form.errors)
            return redirect("register")
        except Exception as e:
            messages.error(request, str(e))
            return redirect("register")


# 로그인 화면 
class UserLogin(TemplateView):
    template_name = "user/login.html"

    def get_context_data(self):
        context = super().get_context_data()
        context['form'] = LoginForm()
        return context

    def post(self, request):
        try:
            name = request.POST.get("name").strip()
            password = request.POST.get("password").strip()

            # request 객체에 로그인한 사용자 정보 추가 
            login(request, user_by_valid_login(
                                name=name, password=password))  
            return redirect("task-list")
        except Exception as e:
            messages.error(request, str(e))
            return redirect("login")

         
# 로그아웃 기능 
class UserLogout(View):
    def get(self, request):
        logout(request) # request.user 데이터 제거 
        return redirect("login")

