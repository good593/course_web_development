from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
def user_login(request):
    """로그인 화면 이동"""
    if request.user.is_authenticated:
        # 로그인 이미 성공하였을 때,
        return redirect("todolist")

    return render(
        request=request,
        template_name="user/login.html"
    )

def req_login(request):
    """
    로그인 요청
    - 성공: todolist 페이지 이동 
    - 실패: 로그인 페이지 이동 
    """
    if request.method != "POST":
        # 올바른(POST) 요청이 아닐 때, 
        messages.error(request, "[에러] 올바른 로그인 요청을 해주세요.")
        return redirect("user-login")
    elif request.user.is_authenticated:
        # 로그인 이미 성공하였을 때,
        return redirect("todolist")

    username = request.POST.get("username").strip()
    password = request.POST.get("password").strip()
    
    # 만약 DB에 해당 유저가 있다면, user 객체 리턴 
    # 그렇지 않다면, None 리턴 
    is_user = authenticate(username=username, password=password)
    if not is_user:
        messages.error(request, "[에러] 해당 유저 없어요.")
        return redirect("user-login")

    login(request, is_user)
    return redirect("todolist")

def user_register(request):
    """등록 페이지 이동"""
    if request.user.is_authenticated:
        # 로그인 이미 성공하였을 때,
        return redirect("todolist")

    return render(
        request=request,
        template_name="user/register.html"
    )

def req_register(request):
    """
    등록 요청
    - 성공: 로그인 페이지 이동 
    - 실패: 등록 페이지 이동 
    """
    if request.method != "POST":
        # 올바른(POST) 요청이 아닐 때, 
        messages.error(request, "[에러] 올바른 등록 요청을 해주세요.")
        return redirect("user-login")
    elif request.user.is_authenticated:
        # 로그인 이미 성공하였을 때,
        return redirect("todolist")

    username = request.POST.get("username").strip()
    password = request.POST.get("password").strip()
    email = request.POST.get("email").strip()
    
    # 만약 DB에 해당 유저가 있다면, user 객체 리턴 
    # 그렇지 않다면, None 리턴 
    is_user = authenticate(username=username, password=password)
    if is_user:
        messages.error(request, "[에러] 이미 유저 있어요.")
        return redirect("user-register")

    new_user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    new_user.save() # insert & update 
    return redirect("user-login")

def user_logout(request):
    """로그아웃 요청"""
    logout(request)
    return redirect("user-login")
