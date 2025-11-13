from django.urls import path

from .views import (
    UserRegister, UserLogin, UserLogout
)

# http://locahost:8000/user/*
urlpatterns = [
    # http://locahost:8000/user/register/
    path("register/", UserRegister.as_view(), name="user-register"),
    # http://locahost:8000/user/login/
    path("login/", UserLogin.as_view(), name="user-login"),
    # http://locahost:8000/user/logout/
    path("logout/", UserLogout.as_view(), name="user-logout"),
]
