from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import authenticate, login, logout

def user_register(request):
    # 로그인한 상태에서 로그인 페이지로 접근할 경우
    if request.user.is_authenticated:
        return redirect('todolist-todolist')
    
    elif request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        email = request.POST.get('email').strip()
        
        # 이미 존재하는 사용자 체크
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, '이미 존재하는 사용자입니다.')
            return redirect('user-register')
        elif not username or not password or not email:
            messages.error(request, '아이디, 이메일, 비밀번호를 입력하세요.')
            return redirect('user-register')
        
        new_user = CustomUser.objects.create_user(username=username, password=password, email=email)
        new_user.save()
        messages.success(request, '회원가입이 완료되었습니다.')
        return redirect('user-login')
    
    return render(request, 'user/register.html')

# 로그인
def user_login(request):
    # 로그인한 상태에서 로그인 페이지로 접근할 경우
    if request.user.is_authenticated:
        return redirect('todolist-todolist')
    
    elif request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        
        # 사용자 인증
        user = authenticate(request, username=username, password=password)
        
        if not user:
            messages.error(request, '아이디 또는 비밀번호가 틀렸습니다.')
            return redirect('user-login')
        
        # 로그인 성공
        login(request, user)
        return redirect('todolist-todolist')
    
    return render(request, 'user/login.html')

# 로그아웃
def user_logout(request):
    # 로그아웃 요청
    logout(request)
    return redirect('user-login')