---
style: |
  img {
    display: block;
    float: none;
    margin-left: auto;
    margin-right: auto;
  }
marp: true
paginate: true
---
# MySQL 적용
- create_db_user_of_mysql.sql 참고 

---
### 단계1: 데이터베이스 생성
```sql
create database django_db;
show databases;
```
![alt text](image.png)

---
### 단계2: 사용자 계정 생성
```sql
use mysql;

create user 'django_root'@'%' identified by 'django_root1!';
select * from user;
```
![alt text](image-1.png)

---
### 단계3: 사용자 권한 부여
```sql
grant all privileges on django_db.* to 'django_root'@'%';
flush privileges; -- 새로운(수정된) 권한 적용 
```
![alt text](image-2.png)

---
### 단계4: mysql 드라이버 설치
```shell
$ (.venv) pip install pymysql
```
![alt text](image-3.png)

---
### 단계5: django with mysql
- config/settings.py에 mysql 설정 추가 
```python
import pymysql 
pymysql.install_as_MySQLdb()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "django_db", # 데이터베이스 이름 
        "USER": "django_root", # 유저 아이디
        "PASSWORD": "django_root1!", # 유저 비번
        "HOST": "localhost", # host 주소
        "PORT": "3306" # port 번호 
    }
}
```

---
# [Models](https://docs.djangoproject.com/ko/5.0/topics/db/models/) 
- 모델은 데이터에 대한 단 하나의 정보의 소스입니다. 
- 모델은 저장하고 있는 데이터의 필수적인 필드와 동작을 포함하고 있습니다. 
- 일반적으로, 각각의 모델은 하나의 데이터베이스 테이블에 매핑됩니다.

---
### 단계1: todo 생성 
- todoList.models.py
```python
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    todo_name = models.CharField(max_length=1000)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.todo_name
```
---
### 단계2: 마이그레이션(migration)
- 테이블 및 필드의 생성, 삭제, 변경 등과 같은 스키마 정보에 대한 변경사항을 저장(기억)
- app 폴더 아래에 migrations 폴더에 마이그레이션 정보 저장 
```shell
$ (.venv) python manage.py makemigrations 
```



---
# Django 관리자 페이지 

---
### 단계1: Admin 계정 
- admin 생성 
```shell
python manage.py createsuperuser 
```
- admin 계정 비번 변경 
```shell
python manage.py changepassword admin
```

---
### 단계2: Model 등록 
- 생성한 app의 admin.py
```python
from django.contrib import admin
from .models import todo

# Register your models here.
admin.site.register(todo)
```

---
# 참고문서 
### 유튜브 동영상
- https://www.youtube.com/watch?v=EpqVtxTyTT8&list=PL8Loxdz4U5rqhjG3xAeE5SAmeeJJ5zQY0&index=2
### github
- https://github.com/deji12/todo_tutorial

