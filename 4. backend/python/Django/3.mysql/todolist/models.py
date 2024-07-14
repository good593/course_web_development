from django.db import models

# Create your models here.
class todo(models.Model):
    todo_name = models.CharField(max_length=1000)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.todo_name
