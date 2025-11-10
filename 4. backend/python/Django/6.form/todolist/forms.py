from django import forms 

from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task 
        # 화면에 프린트할 컬럼들 
        fields = [
            'title', 'description', 'complete'
        ]