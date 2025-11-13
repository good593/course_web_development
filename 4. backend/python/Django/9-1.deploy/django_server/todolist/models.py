from django.db import models

from user.models import CustomUser

# Create your models here.
class Todo(models.Model):
    todo_name = models.CharField(max_length=500)
    status = models.BooleanField(default=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.todo_name
    
    class Meta:
        db_table = 'todo' # 생성될 테이블명 

