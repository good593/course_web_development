from django import forms 
from .models import Task 

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task 
        # 모델에 정의한 컬럼들 중에서 화면에 표현한 컬럼들 
        fields = ['title', 'description', 'complete'] 
