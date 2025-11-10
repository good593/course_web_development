import email
from django import forms 
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser 

class LoginForm(forms.ModelForm):
    """Template에 사용할 로그인 화면 클래스"""
    class Meta:
        model = CustomUser
        fields = ['name', 'password'] # 화면에 프린트될 컬럼들 
        widgets = {
            'password': forms.PasswordInput() # 화면에 입력될 때, 마스킹(*) 처리됨.
        }

class RegisterForm(UserCreationForm):
    """Template에 사용할 가입 화면 클래스"""
    # 추가로 입력 받아야 하는 변수들 선언 
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = [ # 아이디(name)과 비번(password1, password2)는 필수 
            'name', 'email', 'password1', 'password2'
        ] 
