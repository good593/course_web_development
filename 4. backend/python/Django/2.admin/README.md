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
# 관리자 페이지 접속하기 

---
### 단계1: Create Django
1. 가상환경 만들자
2. 장고 프로젝트 생성
3. 장고 앱 생성 
4. templates 설정
5. static 설정

---
### 단계2: 서버 기동
- 마이그레이션(migration)
    - 테이블 및 필드의 생성, 삭제, 변경 등과 같은 스키마 정보에 대한 변경사항을 저장(기억)
    - app 폴더 아래에 migrations 폴더에 마이그레이션 정보 저장 
```shell
$ (.venv) python manage.py makemigrations 
```
- Database에 마이그레이션 정보 반영 
    - 마이크레이션에 저장된 스키마 정보를 이용하여 Database의 테이블 생성/삭제/변경 진행 
```shell
$ (.venv) python manage.py migrate
```
- server 실행 
```shell
$ (.venv) python manage.py runserver
``` 
---
### 단계3: 관리자 페이지 접속하기 
- config.urls.py
  - 관리자 페이지 접속 정보를 확인할 수 있음
```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

---
- [관리자 페이지 접속](http://127.0.0.1:8000/admin/)

![alt text](./img/image.png)

---
### 단계4: 관리자 계정 생성을 위한 테이블 생성 
- Database에 마이그레이션 정보 반영 
    - 마이크레이션에 저장된 스키마 정보를 이용하여 Database의 테이블 생성/삭제/변경 진행 
```shell
$ (.venv) python manage.py migrate
```
![alt text](./img/image-1.png)

---
### 단계5: [SQLite DB에 생성된 테이블 확인](https://docs.python.org/ko/3.8/library/sqlite3.html) 
> SQLite는 파이썬에 기본적으로 내장되어 있는 데이터베이스이다. 
- SQLite 설치  

![alt text](./img/image-2.png)

---
- SQLite DB 연결

![alt text](./img/image-3.png)
![alt text](./img/image-4.png)

---
- 테이블 정보 확인 

![alt text](./img/image-5.png)

---
### [단계6: Superuser 만들기](https://developer.mozilla.org/ko/docs/Learn/Server-side/Django/Admin_site#superuser_%EB%A7%8C%EB%93%A4%EA%B8%B0)
- 관리자 사이트에 로그인하기 위해서는, 직원(Staff) 상태가 활성화 된 사용자 계정이 있어야 합니다. 
- 레코드들을 보고 생성하기 위해서는 이 사용자가 모든 객체들을 관리하기 위한 허가가 있어야 합니다. 
- 사이트에 대한 모든 접속 권한과 필요한 허가를 가진 "superuser" 계정을 manage.py를 사용해서 만들 수 있습니다.

---
```shell
(.venv) python manage.py createsuperuser
```
![alt text](./img/image-6.png)

---
- SQLite에서 조회 

![alt text](./img/image-7.png)

---
### 단계7: 관리자 페이지 접속 및 로그인하기 
- server 실행 
```shell
$ (.venv) python manage.py runserver
``` 
- [관리자 페이지 접속](http://127.0.0.1:8000/admin/)

![alt text](./img/image-8.png)

---
- 접속 성공 

![alt text](./img/image-9.png)

---
### 단계8: admin 계정 비번 변경 
```shell
$ (.venv) python manage.py changepassword admin
```
![alt text](./img/image-17.png)

---
# 관리자 페이지에서 사용자 생성하기  

---
### 단계1: Users 페이지 이동 
![alt text](./img/image-10.png)

---
### 단계2: 사용자 생성하기 
![alt text](./img/image-11.png)

---
### 단계3: 사용자 확인 
![alt text](./img/image-12.png)

---
- SQLite DB에서 확인 

![alt text](./img/image-13.png)

---
# [Models(스키마) 등록하기](https://developer.mozilla.org/ko/docs/Learn/Server-side/Django/Admin_site#models_%EB%93%B1%EB%A1%9D%ED%95%98%EA%B8%B0) 

---
### 단계1: Model(스키마) 정의/생성
- todolist.models.py
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
### 단계2: Model 등록하기 
- todolist.admin.py
```python
from django.contrib import admin
from .models import todo

# Register your models here.
admin.site.register(todo)
```

---
### 단계3: 변경된 스키마 적용 및 서비 실행 
- 마이그레이션(migration)
    - 테이블 및 필드의 생성, 삭제, 변경 등과 같은 스키마 정보에 대한 변경사항을 저장(기억)
    - app 폴더 아래에 migrations 폴더에 마이그레이션 정보 저장 
```shell
$ (.venv) python manage.py makemigrations 
```
![alt text](./img/image-14.png)

---
- Database에 마이그레이션 정보 반영 
    - 마이크레이션에 저장된 스키마 정보를 이용하여 Database의 테이블 생성/삭제/변경 진행 
```shell
$ (.venv) python manage.py migrate
```
![alt text](./img/image-16.png)

---
- server 실행 및 관리자 페이지 접속 
```shell
$ (.venv) python manage.py runserver
``` 
![alt text](./img/image-15.png)






