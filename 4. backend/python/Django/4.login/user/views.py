from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def user_register(request):
    # 너 로그인 했니?
    if request.user.is_authenticated:
        return redirect("todo-list")
    # 너 가입 요청하는 거니?
    elif request.method == "POST":
        uname = request.POST.get("username")
        uemail = request.POST.get("email")
        upwd = request.POST.get("password")

        # 비밀번호 길이가 3이상이어야함
        if len(upwd) < 3:
            messages.error(request, "Password must be at least 3 characters")
            return redirect("user-register")

        # User.objects -> db에 있는 user 테이블 모든 데이터
        # filter(username=uname) -> 컬럼(username)의 데이터가 브라우저입력값(uname) 같은 데이터 조회  
        # get_all_users_by_username 
        # -> user 테이블 데이터 중 username 컬럼 값이 uname과 같은 데이터들이 담겨 있음 
        # -> [User, User, User, ...]
        get_all_users_by_username = User.objects.filter(username=uname)
        if get_all_users_by_username:
            messages.error(request, "Error, username already exists, User another.")
            return redirect("user-register")

        # 신규회원 등록 프로세스 
        # User 인스턴스 생성 -> User 테이블에는 저장 x
        new_user = User.objects.create_user(
            username=uname, email=uemail, password=upwd
        )

        # User 인스턴스의 정보를 User 테이블에 저장 o 
        new_user.save()

        messages.success(request, "User successfully created, login now")
        return redirect("user-login")

    # 가입 화면으로 이동...
    else:
        return render(request, "user/register.html", {})


def user_login(request):
    # 로그인 했니?
    if request.user.is_authenticated:
        return redirect("todo-list")
    # POST method 온거니? (로그인 요청한거니?)
    elif request.method == "POST":
        # login.html에서 입력한 값이 변수에 저장됨
        username = request.POST.get("username")
        pwd = request.POST.get("password")

        # 입력한 값을 바탕으로 인증 진행(db에 해당 유저가 있는지 확인) 
        # -> 성공: validate_user(user 인스턴스(아이디, 이름, 이메일 등))
        # -> None
        validate_user = authenticate(username=username, password=pwd)
        if validate_user is not None:
            # request에 validate_user 인스턴스를 저장(추가)
            login(request, validate_user)
            return redirect("todo-list")
        else:
            messages.error(request, "Erro, wrong user details or user does not exist")
            return redirect("user-login")
    # 그냥 온 손님들...
    else:
        return render(request, "user/login.html", {})


def user_logout(request):
    logout(request)
    return redirect("user-login")
