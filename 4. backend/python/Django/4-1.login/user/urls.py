from django.urls import path 

from .views import (
    user_login, req_login,
    user_register, req_register,
    user_logout
)

# http://127.0.0.1:8000/user/*
urlpatterns = [
    # http://127.0.0.1:8000/user/login/
    path("login/", user_login, name="user-login"),

    # http://127.0.0.1:8000/user/req-login/
    path("req-login/", req_login, name="req-login"),

    # http://127.0.0.1:8000/user/register/
    path("register/", user_register, name="user-register"),

    # http://127.0.0.1:8000/user/req-register/
    path("req-register/", req_register, name="req-register"),

    # http://127.0.0.1:8000/user/logout/
    path("logout/", user_logout, name="user-logout"),
]