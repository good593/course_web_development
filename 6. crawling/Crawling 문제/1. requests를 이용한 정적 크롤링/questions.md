## requests 문제

---
### 문제 1. GET 요청을 이용한 데이터 가져오기
- requests 모듈을 사용하여 JSONPlaceholder의 posts API에서 게시글 목록을 가져오세요.
- 가져온 데이터 중 userId가 1인 게시글만 필터링하여 출력하세요.
- 요청 URL:
  ```shell
  "https://jsonplaceholder.typicode.com/posts"
  ```

---
### 문제 2. POST 요청을 사용하여 데이터 전송하기
- requests.post()를 사용하여 아래 JSON 데이터를 서버에 전송해 보세요.
- 응답으로 돌아온 JSON을 출력하세요.
- 요청 URL:
  ```shell
  "https://jsonplaceholder.typicode.com/posts"
  ```
- 전송할 JSON 데이터:
  ```json
  {
    "title": "Test Post",
    "body": "This is a test post using Python requests.",
    "userId": 101
  }
  ```

---
### 문제 3. 에러 처리 및 타임아웃 설정
- 다음 URL로 GET 요청을 보내되, 타임아웃을 2초로 설정하세요.
- 만약 2초 안에 응답이 오지 않으면 "요청이 타임아웃되었습니다."라는 메시지를 출력하세요.
- 또한, 상태 코드가 200이 아닐 경우 에러 메시지를 출력하세요.
- 요청 URL:
  ```shell
  "https://httpbin.org/delay/5"
  ```


