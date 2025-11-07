from django import forms 
from django.contrib.auth.forms import UserCreationForm 

from .models import CustomUser

class CustomLoginForm(forms.ModelForm):
    """Template에 사용할 로그인 화면 클래스"""
    class Meta:
        model = CustomUser
        fields = ['name', 'password'] # 화면에 표현될 컬럼리스트 
        widgets = {
            'password': forms.PasswordInput() # 화면에 입력할 때, *로 표시됨. 
        }

class CustomRegisterForm(UserCreationForm):
    """Template에 사용할 가입 화면 클래스"""
    # name(아이디), password(비번)을 제외한 추가 입력이 필요한 경우 
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        # 화면에 표현될 컬럼리스트
        fields = ['name', 'email', 'password1', 'password2']  
