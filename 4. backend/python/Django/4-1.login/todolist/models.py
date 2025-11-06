from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class todo(models.Model):
    todo_name = models.CharField(max_length=500)
    status = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.todo_name 
