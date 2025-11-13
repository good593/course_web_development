from django.shortcuts import redirect 
from django.urls import reverse

class AuthRedirectMiddleware:
    """
    인증/인가에 대한 화면 접근 제어를 하는 미들웨어 
    [중요] settings.py에 추가해야함 
        MIDDLEWARE = [
            ...,
            'user.middleware.AuthRedirectMiddleware' # 마지막 아래에 추가 
        ]
    """
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        url_login = reverse("user-login")
        url_register = reverse("user-register")
        url_todolist = reverse("todolist")

        # 로그인을 했을 때,
        if request.user.is_authenticated:
            # 로그인 화면 또는 가입 화면으로 요청한 경우,
            if request.path in [url_login, url_register]:
                return redirect(url_todolist) # todolist 화면으로 강제 이동 
        
        # 로그인을 하지 않았는데, 로그인 화면 또는 가입 화면이 아닌 다른 화면으로 요청한 경우,
        elif request.path not in [url_login, url_register]:
            return redirect(url_login) # 로그인 화면으로 강제 이동

        # 그외의 모든 요청은 그대로 처리 
        response = self.get_response(request)
        return response

