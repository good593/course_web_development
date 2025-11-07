from django.db import models
from user.models import CustomUser

class todo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    todo_name = models.CharField(max_length=1000)
    status = models.BooleanField(default=False)
    created_dt = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.todo_name
    
    class Meta:
        db_table = 'todo'
        ordering = ['status', '-created_dt']