from django.db import models
from user.models import CustomUser

# Create your models here.
class Task(models.Model):
    # 등록한 유저 
    custom = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # 제목
    title = models.CharField(max_length=50)
    # Task 설명 
    description = models.TextField(null=True, blank=True)
    # Task 완료 유무
    complete = models.BooleanField(default=False)
    # 생성된 날짜 
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'task'                   # 생성될 테이블명
        ordering = ['complete', '-created'] # 조회 정렬(order by)
