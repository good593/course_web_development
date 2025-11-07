# user/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class AuthRedirectMiddleware:
    """
    로그인 상태에 따라 접근을 제어하는 미들웨어
    [중요] settings.py에 추가해야함 
        MIDDLEWARE = [
            ...
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'user.middleware.AuthRedirectMiddleware', # 커스텀 미들웨어 마지막 아래에 추가
        ]
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 로그인/회원가입 URL 경로
        login_url = reverse("user-login")
        register_url = reverse("user-register")
        todolist_url = reverse("todolist")

        # 요청 전 처리 ------------------------------
        if not request.user.is_authenticated:
            # 비로그인 상태에서 todolist 등 보호된 페이지 접근 → 로그인 페이지로 이동
            if request.path not in [login_url, register_url]:
                return redirect(login_url)
        
        # 로그인 상태에서 login, register 페이지 접근 시 → todolist로 이동
        elif request.path in [login_url, register_url]:
                return redirect(todolist_url)

        # 다음 미들웨어 또는 뷰 실행
        response = self.get_response(request)
        return response
