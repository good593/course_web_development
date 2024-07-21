from django.db import models
from user.models import Custom 

# Create your models here.
class Task(models.Model):
    custom = models.ForeignKey(Custom, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title 
    
    class Meta:
        ordering = ['complete', '-created']

