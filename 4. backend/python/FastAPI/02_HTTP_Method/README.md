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
# [HTTP Method 이해](https://developer.mozilla.org/ko/docs/Web/HTTP/Reference/Methods)
- HTTP(Hypertext Transfer Protocol)는 클라이언트와 서버 간 통신을 위한 통신 규칙 세트 또는 프로토콜입니다. 
- HTTP는 요청 메서드를 정의하여, 주어진 리소스에 수행하길 원하는 행동을 나타냅니다.

---

## 1. HTTP 메서드 전체 개요

HTTP 메서드는 서버에게 **"무엇을 하고 싶은지"** 전달하는 동사다.

| 메서드 | 역할 | 멱등성 | Body |
|--------|------|--------|------|
| **GET** | 조회 | O | X |
| **POST** | 생성 | X | O |
| **PUT** | 전체 수정 | O | O |
| **PATCH** | 부분 수정 | X | O |
| **DELETE** | 삭제 | O | X |

---
## 2. GET vs POST 핵심 차이

---
### GET
```
GET /search?keyword=fastapi&page=1 HTTP/1.1
Host: api.example.com
```

- 데이터를 **URL에 포함** (Query String)
- **조회 전용** — 서버 상태를 바꾸지 않는다
- 브라우저 히스토리/북마크 가능
- URL 길이 제한 있음 (~2000자)
- **민감한 정보 전송 금지** (URL이 로그에 남음)

---
### POST
```
POST /users HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
    "name": "홍길동",
    "password": "secret123"
}
```

- 데이터를 **Request Body에 포함**
- **생성 / 처리** 목적
- URL에 데이터가 노출되지 않음
- 데이터 크기 제한 없음
- 민감한 정보 전송 가능

---
### 비교 요약

| 항목 | GET | POST |
|------|-----|------|
| 데이터 위치 | URL Query String | Request Body |
| 데이터 크기 | 제한 있음 | 제한 없음 |
| 보안 | URL에 노출 | Body에 숨김 |
| 캐싱 | 가능 | 불가 |
| 목적 | 조회 | 생성/처리 |
| 멱등성 | O | X |

---
## [3. HTTP 상태 코드](https://developer.mozilla.org/ko/docs/Web/HTTP/Reference/Status)
> 서버가 클라이언트에게 **"결과가 어떻게 됐는지"** 알려주는 숫자 코드

---
### 2xx — 성공

| 코드 | 이름 | 언제 사용 |
|------|------|----------|
| **200** | OK | 일반적인 성공 (GET, PUT, PATCH) |
| **201** | Created | 리소스 생성 성공 (POST) |
| **204** | No Content | 성공했지만 응답 본문 없음 (DELETE) |

---
### 4xx — 클라이언트 오류

| 코드 | 이름 | 언제 사용 |
|------|------|----------|
| **400** | Bad Request | 잘못된 요청 (형식 오류, 비즈니스 로직 위반) |
| **401** | Unauthorized | 인증 필요 |
| **403** | Forbidden | 권한 없음 |
| **404** | Not Found | 리소스 없음 |
| **422** | Unprocessable Entity | 데이터 검증 실패 (FastAPI 기본) |

---
### 5xx — 서버 오류

| 코드 | 이름 | 언제 사용 |
|------|------|----------|
| **500** | Internal Server Error | 서버 내부 오류 |
| **503** | Service Unavailable | 서버 일시 중단 |

---
## 4. HTTP Request 구성 요소

```
POST /users/42/orders?notify=true HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
    "product_id": 10,
    "quantity": 3
}
```

---
| 구성 요소 | 예시 | 설명 |
|-----------|------|------|
| **Method** | `POST` | 행위 |
| **Path** | `/users/42/orders` | 리소스 경로 |
| **Path Parameter** | `42` | URI 내 변수 |
| **Query Parameter** | `notify=true` | URL `?` 뒤 키=값 |
| **Header** | `Authorization: Bearer ...` | 메타데이터 (인증, 타입 등) |
| **Body** | `{"product_id": 10, ...}` | 전송 데이터 |

---
## 5. 실습

### 실습 서버 실행

```bash
uv run uvicorn main:app --reload --port 8001
```

---
### [Swagger UI에서 요청 분석](https://swagger.io/tools/swagger-ui/)
> Swagger UI는 개발자가 RESTful API 문서를 시각적으로 확인하고, 별도의 테스트 도구(예: Postman) 없이도 웹 화면에서 직접 API를 호출하고 테스트할 수 있도록 해주는 오픈소스 프레임워크입니다.

1. `http://127.0.0.1:8001/docs` 접속
2. 엔드포인트 클릭 → **Parameters** 확인 (Path / Query 구분)
3. **Request body** 섹션 확인
4. "Try it out" → "Execute" → **Response** 분석
   - Response Code
   - Response Headers
   - Response Body

---
## 6. REST URI 설계 규칙

### 좋은 URI vs 나쁜 URI

```
# 리소스는 명사, 복수형 사용
[OK]  GET  /articles
[OK]  GET  /articles/1
[OK]  POST /articles

[BAD] GET  /getArticles
[BAD] GET  /article/1       (단수)
[BAD] POST /createArticle
```

---
### 계층 구조 표현
```
# 계층 구조 표현
[OK]  GET /users/42/orders        (42번 유저의 주문 목록)
[OK]  GET /users/42/orders/7      (42번 유저의 7번 주문)
```

### 필터/정렬/페이지는 Query Parameter
```
# 필터/정렬/페이지는 Query Parameter
[OK]  GET /articles?category=tech&sort=latest&page=2
[BAD] GET /articles/tech/latest/page/2
```

---
### 상태 코드와 메서드 조합

```
POST   /users          → 201 Created
GET    /users          → 200 OK
GET    /users/99       → 200 OK (있을 때), 404 Not Found (없을 때)
PUT    /users/99       → 200 OK
DELETE /users/99       → 204 No Content
POST   /users (중복)   → 400 Bad Request 또는 409 Conflict
```
