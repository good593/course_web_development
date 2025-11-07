from django.urls import path 

from .views import (
    UserRegister, UserLogin, UserLogout
)

# http://localhost:8000/user/*
urlpatterns = [
    # http://localhost:8000/user/register/
    path("register/", UserRegister.as_view(), name="user-register"),
    # http://localhost:8000/user/login/
    path("login/", UserLogin.as_view(), name="user-login"),
    # http://localhost:8000/user/logout/
    path("logout/", UserLogout.as_view(), name="user-logout")
]