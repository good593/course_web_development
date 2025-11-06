from django.urls import path 

from .views import (
    UserRegister, UserLogin, UserLogout 
)

# /user/*
urlpatterns = [
    # /user/register/
    path("register/", UserRegister.as_view(), name="user-register"),
    # /user/login/
    path("login/", UserLogin.as_view(), name="user-login"),
    # /user/logout/
    path("logout/", UserLogout.as_view(), name="user-logout"),
]
