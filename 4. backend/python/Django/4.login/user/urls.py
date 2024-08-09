from django.urls import path
from .views import user_register, user_login, user_logout

# 요청 url: http://localhost:8000/user/login/
# localhost/user/
urlpatterns = [
    # localhost/user/register/
    path("register/", user_register, name="user-register"),
    # localhost/user/login/
    path("login/", user_login, name="user-login"),
    # localhost/user/logout/
    path("logout/", user_logout, name="user-logout"),
]
