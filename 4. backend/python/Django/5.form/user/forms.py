from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Custom 

class CustomForm(forms.ModelForm):
    class Meta:
        model = Custom  # 사용할 모델
        fields = ['name', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

class CustomCreationForm(UserCreationForm):
    email=forms.EmailField()

    class Meta:
        model = Custom
        fields = ('name', 'email', 'password1', 'password2')


