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
# [Custom User Model](https://docs.djangoproject.com/ko/5.0/topics/auth/customizing/#customizing-authentication-in-django)

---
### [BaseUserManager](https://docs.djangoproject.com/ko/5.0/topics/auth/customizing/#django.contrib.auth.models.BaseUserManager)
- User를 생성할 때 사용하기 위해서 상속받아야하는 클래스이다. 
```python
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    ...
```
- create_user(): User 생성하는 함수 
```python
class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
       ...
```
- create_superuser(): 관리자 User 생성하는 함수 
```python
class UserManager(BaseUserManager):
    def create_superuser(self, email, nickname,password ): 
       ...
```

---
### [AbstractBaseUser](https://docs.djangoproject.com/ko/5.0/topics/auth/customizing/#specifying-a-custom-user-model)
- 사용자 모델(User) 클래스를 생성하기 위해서 상속받아야 하는 클래스이다.
- USERNAME_FIELD
  - user model에서 사용할 고유 식별자로 필수로 입력해 주어야 합니다.
- REQUIRED_FIELDS
  - user model 에서 요구되는 필드의 모두 포함합니다만 “USERNAME_FIELD” 혹은 “Password” 필드는 제외합니다.
```python
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    identifier = models.CharField(max_length=40, unique=True)
    date_of_birth = models.DateField()
    height = models.FloatField()
    ...

    USERNAME_FIELD = "identifier"
    REQUIRED_FIELDS = ["date_of_birth", "height"]
```

---
### [PermissionsMixin](https://docs.djangoproject.com/ko/5.0/topics/auth/customizing/#custom-users-and-permissions)
- Django에서 제공하는 사용자 권한을 사용하기 위해서 상속받아야 하는 클래스이다. 
- is_superuser
  - 불리언. 명시적으로 할당하지 않고 모든 권한을 사용자가 갖도록 지정한다.
```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(AbstractBaseUser,PermissionsMixin):    
    is_superuser = models.BooleanField(default=False) 
    ...
```
---
### [settings.py](https://docs.djangoproject.com/ko/5.0/topics/auth/customizing/#substituting-a-custom-user-model)
- AUTH_USER_MODEL = '[앱명].[커스텀 모델명]'
```python
AUTH_USER_MODEL = "user.User"
```

---
# [Forms](https://docs.djangoproject.com/ko/5.0/topics/forms/#forms-in-django)
- 폼은 쉽게 말해 페이지 요청 시 전달되는 파라미터들을 쉽게 관리하기 위해 사용하는 클래스이다. 
- 폼은 필수 파라미터의 값이 누락되지 않았는지, 파라미터의 형식은 적절한지 등을 검증할 목적으로 사용한다. 
- 이 외에도 HTML을 자동으로 생성하거나 폼에 연결된 모델을 이용하여 데이터를 저장하는 기능도 있다.

---
### [Django Forms 처리 프로세스](https://developer.mozilla.org/ko/docs/Learn/Server-side/Django/Forms#django_%ED%8F%BC_%EC%B2%98%EB%A6%AC_%EA%B3%BC%EC%A0%95)
![alt text](image.png)

---
위의 다이어그램에 기반하여, Django 폼이 주요하게 다루는 것은 다음과 같다. :

1. `사용자가 처음으로 폼을 요청할 때 기본 폼을 보여준다.`
    - 폼은 비어있는 필드가 있을 수 있다 (예를 들면, 새로운 책을 등록할 경우) 아니면 초기값으로 채워진 필드가 있을 수도 있다. ( 예를 들면, 기존의 책을 수정하거나, 흔히 사용하는 초기값이 있을경우)
    - 이 시점의 폼은 (초기값이 있긴해도) 유저가 입력한 값에 연관되지 않았기에 unbound 상태라고 불린다.
2. `제출 요청으로 부터 데이타를 수집하고 그것을 폼에 결합한다.`
    - 데이타를 폼에 결합(binding) 한다는 것은 사용자 입력 데이타와 유효성을 위반한 경우의 에러메시지가 폼을 재표시할 필요가 있을 때 준비되었다는 의미이다.

---
3. `데이타를 다듬어서 유효성을 검증한다.`
    - 데이타를 다듬는다는 것은 사용자 입력을 정화(sanitisation) 하고 (예를 들면, 잠재적으로 악의적인 콘덴츠를 서버로 보낼수도 있는 유효하지 않은 문자를 제거하는 것) python에서 사용하는 타입의 데이타로 변환하는 것이다.
    - 유효성검증은 입력된 값이 해당 필드에 적절한 값인지 검사한다. (예를 들면, 데이타가 허용된 범위에 있는 값인지, 너무 짧거나 길지 않은지 등등)
4. `입력된 어떤 데이타가 유효하지 않다면, 폼을 다시 표시하는데 이번에는 초기값이 아니라 유저가 입력한 데이타와 문제가 있는 필드의 에러 메시지와 함께 표시한다.`
5. `입력된 모든 데이타가 유효하다면, 요청된 동작을 수행한다. (예를 들면, 데이타를 저장하거나, 이메일을 보내거나, 검색결과를 반환하거나, 파일을 업로딩하는 작업 등등)`
6. `일단 모든 작업이 완료되었다면, 사용자를 새로운 페이지로 보낸다.`

---
### [Form vs Model Form](https://wayhome25.github.io/django/2017/05/06/django-form/)
- `Form(일반 폼)`: 직접 필드 정의, 위젯 설정이 필요
- `Model Form(모델 폼)`: 모델과 필드를 지정하면 모델폼이 자동으로 폼 필드를 생성
```python
from django import forms
from .models import Post

# Form (일반 폼)
class PostForm(forms.Form):
	title = forms.CharField()
	content = forms.CharField(widget=forms.Textarea)

# Model Form (모델 폼)
class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['title', 'content']
```
---
### [Cleaning and validating fields](https://docs.djangoproject.com/en/5.0/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other)
```python
from django import forms
from django.core.exceptions import ValidationError

class ContactForm(forms.Form):
    # Everything as before.
    ...

    def clean(self):
        cleaned_data = super().clean()
        cc_myself = cleaned_data.get("cc_myself")
        ...
```

---
### [Form Fields](https://docs.djangoproject.com/ko/5.0/ref/forms/fields/)
- Model Fields: Database Field들을 파이썬 클래스화 
- Form Fields: HTML Form Field들을 파이썬 클래스화

![alt text](image-1.png)

---
# [로그인 유무를 이용한 사용자 접근 제한](https://docs.djangoproject.com/ko/5.0/topics/auth/default/#limiting-access-to-logged-in-users)

---
### is_authenticated
```python
from django.shortcuts import render

def my_view(request):
    if not request.user.is_authenticated:
        return render(request, "myapp/login_error.html")
    # ...
```

---
### login_required
- settings.py
```python
...
LOGIN_URL = "/user/login/"
```
- views.py
```python
from django.contrib.auth.decorators import login_required

@login_required
def task_list(request):
    template_name = 'todoList/task_list.html' 
    ...
```

---
# [template](https://docs.djangoproject.com/en/5.0/ref/templates/language/)
![alt text](image-2.png)

---
### Model
- 유저가 사용할 데이터를 정의하고 관리하는데 DB에 저장되는 데이터를 의미힌다.
### template
- 장고는 뷰에서 로직을 처리한 후 html 파일을 context와 함께 렌더링하는데 이 때의 html 파일을 템플릿이라 칭합니다.
### View
- client Request(요청)에 따라 적절한 로직을 수행하여 결과를 템플릿으로 렌더링하며 응답합니다.
### URL conf
- URL 패턴을 정의해서 URL과 View를 매핑하는 단계이다.

---
# 프로젝트 실행 

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
---



---
# 참고문서 
### github
- https://github.com/divanov11/Django-To-Do-list-with-user-authentication/tree/d798a5917279981f0f68fef068a02a04e94e2734
### article
- https://dennisivy.com/django-class-based-views
### youtube
- https://www.youtube.com/watch?v=llbtoQTt4qw
