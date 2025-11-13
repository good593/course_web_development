from django.http import response
from django.shortcuts import redirect 
from django.urls import reverse 

class AuthRedirectMiddleware:
    """
    인증/인가에 대한 화면 접근 제어를 하는 미들웨어 
    [중요] settings.py에 추가해야함 
        MIDDLEWARE = [
            ...,
            'user.middleware.AuthRedirectMiddleware' # 마지막 위치에 추가 
        ]
    """
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        url_login = reverse("login") # urls의 name값 
        url_register = reverse("register")
        url_task_list = reverse("task-list")

        ###############################
        # 로그인했을 때, 
        ###############################
        if request.user.is_authenticated:
            # 로그인 화면 & 가입 화면 접근 불가..
            if request.path in [url_login, url_register]:
                # todolist 화면으로 강제 이동 
                return redirect(url_task_list)

        ###############################
        # 로그인하지 않았을 때, 
        # 로그인 화면 & 가입 화면이 아닌 다른 화면을 요청하면, 접근 불가...
        ###############################
        elif request.path not in [url_login, url_register]:
            # 로그인 화면으로 강제 이동 
            return redirect(url_login)

        ###############################
        # 정상적인 요청..
        ###############################
        response = self.get_response(request)
        return response
