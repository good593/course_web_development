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
# [Template](https://docs.djangoproject.com/en/4.2/topics/templates/)
- 템플릿은 사용자에게 보여지는 부분이다.
- [장고 템플릿 문법](https://docs.djangoproject.com/en/4.2/ref/templates/language/)에 맞게 python문법을 활용하여 작성할 수 있다.

---
## [Syntax](https://docs.djangoproject.com/en/4.2/topics/templates/#syntax)
- Variables
```html
My first name is {{ first_name }}. My last name is {{ last_name }}.
```

```html
{{ my_dict.key }}
{{ my_object.attribute }}
{{ my_list.0 }}
  ```
---
- [Tags](https://docs.djangoproject.com/en/4.2/ref/templates/builtins/#ref-templates-builtins-tags)
```html
{% if athlete_list %}
    Number of athletes: {{ athlete_list|length }}
{% elif athlete_in_locker_room_list %}
    Athletes should be out of the locker room soon!
{% else %}
    No athletes.
{% endif %}
```
```html
<ul>
{% for athlete in athlete_list %}
    <li>{{ athlete.name }}</li>
{% endfor %}
</ul>
```
---
- [Filters](https://docs.djangoproject.com/en/4.2/ref/templates/builtins/#ref-templates-builtins-filters)
```html
<!-- If value is 4, then the output will be 6. -->
{{ value|add:"2" }}
```
```html
<!-- If value is None, the output will be nothing. -->
{{ value|default_if_none:"nothing" }}
```
```html
<!-- If value is a datetime object (e.g., the result of datetime.datetime.now()), the output will be the string 'Wed 09 Jan 2008'. -->
{{ value|date:"D d M Y" }}
```
---
- HTML Escape:
HTML 내용 중에 <, >, ', ", & 등과 같은 문자들이 있을 경우 이를 그 문자에 상응하는 HTML Entity로 변환해 주어야 하는데, Django 템플릿에서 이러한 작업을 자동으로 처리해 주기 위해 {% autoescape on %} 템플릿 태그나 escape 라는 필터를 사용한다.
```html
<!-- 템플릿 테그 사용 -->
{% autoescape on %}
    {{ content }}
{% endautoescape %}
```
```html
<!-- 템플릿 필터 사용 -->
{{ content|escape }}
```
---
## [csrf_token](https://chagokx2.tistory.com/49)
- CSRF(Cross Site Request Forgery):
웹사이트 취약점 공격의 하나로, 사용자가 자신의 의지와는 무관하게 공격자가 의도한 행위(수정, 삭제, 등록 등)를 특정 웹사이트에 요청하게 하는 공격
  - 이미 사용자가 접속한 상황에서 요청값을 조작하여 사용자가 원하지 않는 action을 보내 웹 어플리케이션을 악용
  - 사용자의 권한에 따라 위험성이 달라짐

---
- Django의 CSRF공격에 대한 방어:
  - CSRF 공격을 방어하기 위한 다양한 방법이 있지만 Django에서는 기본적으로 csrf token을 이용한다.
  - POST 요청에 대해서만 csrf token을 발급하고 체크한다.

```html
<form class="mt-3" action="{% url 'accounts:signup' %}" method="POST" enctype="multipart/form-data">
    {% csrf_token %}
    <div class="form-group">
        <input type="text" class="form-control" id="name" name="name" placeholder="성명">
    </div>
    <button type="submit" class="btn btn-primary">제출하기</button>
</form>
```
---
- 동작과정
  1. 사용자가 해당 페이지에 접속하면 Django에서 자동으로 csrf_token을 클라이언트로 보내어 cookie에 저장
  2. 사용자가 form을 모두 입력한 후 제출버튼을 클릭한다.
  3. form과 cookie의 csrf_token을 함께 POST로 전송한다.
  4. 전송된 token의 유효성을 검증
  5. 유효한 요청이면 요청을 처리
    - token이 유효하지 않거나(없거나 값이 잘못된 경우) 검증 오류 시에는 403 Forbidden Response 반환




















