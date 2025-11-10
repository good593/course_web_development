from django.db import models
from user.models import CustomUser

# Create your models here.
class Task(models.Model):
    custom = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE # 만약 user가 삭제가 되면, Task도 삭제 
    )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task'                   # 데이터베이스에 생성될 테이블명
        ordering = ['complete', '-created'] # 조회 정렬(order by)

    def __str__(self):
        return self.title
