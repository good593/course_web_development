from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# 모델 클래스 특징
# -> 스키마 기능(ERD): 테이블명, 컬럼명, 컬럼 데이터 타입, 컬럼 제약조건, (옵션)테이블간의 상관관계 
    # -> 스키마(ERD) -> 테이블 생성
    # -> python manage.py makemigrations(스키마 파일 생성) & python manage.py migrate(테이블 생성) 
# -> view -> DB의 todo테이블에 있는 데이터를 담는 역할 
class todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    todo_name = models.CharField(max_length=1000)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.todo_name
