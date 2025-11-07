from django.shortcuts import redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from user.models import CustomUser

from .forms import CustomLoginForm, CustomRegisterForm

# Create your views here.
class UserRegister(TemplateView):
    template_name = "user/register.html"

    def get_context_data(self):
        context = super().get_context_data()
        context['form'] = CustomRegisterForm()
        return context

    def post(self, request):
        try:
            # 화면에서 넘어온 데이터를 form 생성 
            form = CustomRegisterForm(request.POST) 
            if form.is_valid(): # 넘어온 데이터 검증
                form.save()     # 검증이 참이면, 테이블에 저장 
                return redirect("login")
            
            # 검증이 오류이면, 
            messages.error(request, form.errors)
            return redirect("register")
        except Exception as e:
            messages.error(request, str(e))
            return redirect("register")

class UserLogin(TemplateView):
    template_name = "user/login.html"

    def get_context_data(self):
        context = super().get_context_data()
        context['form'] = CustomLoginForm()
        return context

    def post(self, request):
        name = request.POST.get("name").strip()
        password = request.POST.get("password").strip() 

        if not CustomUser.objects.filter(name=name).exists():
            messages.error(request, f"{name}는 존재하지 않는 사용자입니다.")
            return redirect("login")

        is_user = authenticate(username=name, password=password)
        if not is_user:
            messages.error(request, f"입력한 비밀번호가 올바르지 않습니다.")
            return redirect("login")
        
        login(request, is_user)
        return redirect("task-list")

class UserLogout(View):
    def get(self, request):
        logout(request)
        return redirect("login")

