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
# [CORS 크로스 도메인](https://oen-blog.tistory.com/46)

---
# [JWT(Json Web Token)](https://juneyr.dev/2018-01-28/making-token-pyjwt)

---
# [Django REST Framework](https://blog.nerdfactory.ai/2021/02/24/creating-an-api-&-collecting-html-elements-with-django-rest-framework.html)

---
# 프로젝트 생성

---
### 단계1: 모듈 추가 설치
```shell
pip install django
pip install djangorestframework
pip install django-cors-headers
pip install PyJWT
pip install pyyaml uritemplate
```

---
### 단계2: 프로젝트 & 앱 생성
```shell
django-admin startproject config . 
python manage.py startapp api
python manage.py startapp user
python manage.py startapp authentication
```

### 단계3: settings.py
- 앱 추가 
```python
INSTALLED_APPS = [
    ...,
    "rest_framework", 
    "corsheaders",
    "api",
    "user",
    "authentication"
]
```

---
- CORS 크로스 도메인 설정
```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", # 맨위에 추가!!
    ...
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
```
- User Model 설정 
```python
AUTH_USER_MODEL = "user.User"
```
- Django REST Framework 설정 
```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'authentication.exceptions.status_code_handler'
}
```

---
### 단계4: User Models 생성 
- user.models.py
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
  name = models.CharField(max_length=255)
  ...
```

---
### 단계5: User Serializer 생성 
- 생성: user.serializer.py
```python
from rest_framework.serializers import ModelSerializer
from .models import User

# api통신때 user정보를 제공하기 위한 객체 
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        ...
```

---
### 단계6: exceptions 처리 
- 생성: authentication.exceptions.py
```python
from rest_framework.views import exception_handler 

def status_code_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.status_code = 777
        ...
```

---
### 단계7: Json Web Token
- 생성: authentication.token.py
```python
import jwt 
import datetime 
import enum 

from rest_framework.exceptions import AuthenticationFailed

class JWT_KEY(enum.Enum):
    RANDOM_OF_ACCESS_KEY = (enum.auto(), 'access_secret', datetime.timedelta(seconds=120), 'HS256', '랜덤한 조합의 키')
    RANDOM_OF_REFRESH_KEY = (enum.auto(), 'refresh_secret', datetime.timedelta(days=2), 'HS256', '랜덤한 조합의 키')

...
```

---
### 단계8: api.views.py 
```python
from rest_framework.authentication import get_authorization_header
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework.exceptions import AuthenticationFailed , APIException

from user.models import User
from user.serializer import UserSerializer
from authentication.token import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token

# Create your views here.
class Register(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
```

---
### 단계9: api.urls.py 
```python
from django.urls import path
from .views import Register, LoginView, HelloWorldView, RefreshView, Logoutview

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('hello-world/', HelloWorldView.as_view(), name='hello-world'),
```

---
### 단계10: config.urls.py 
```python
from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path("api/", include("api.urls"))
]
```

---
# 실행

---
### 단계1: 마이그레이션(migration)
```shell
$ (.venv) python manage.py makemigrations 
```
### 단계2: Database에 마이그레이션 정보 반영 
```shell
$ (.venv) python manage.py migrate
```
### 단계3: server 실행 및 관리자 페이지 접속 
```shell
$ (.venv) python manage.py runserver
``` 


