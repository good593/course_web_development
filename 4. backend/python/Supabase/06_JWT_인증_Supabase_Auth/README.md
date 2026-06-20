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
# JWT 인증과 Supabase Auth 회원가입·로그인

---
## 학습 목표
- JWT(JSON Web Token)의 구조(헤더·페이로드·서명)를 이해한다
- `access_token`과 `refresh_token`의 역할과 만료 시간을 구분한다
- Supabase Auth로 이메일/비밀번호 회원가입과 로그인을 구현한다
- `HTTPBearer`로 Bearer 토큰을 받아 현재 사용자를 결정한다

---
## 1. JWT란 무엇인가
JWT(JSON Web Token)는 서버가 발급하는 **서명된 토큰**입니다.

---
### 토큰 형태

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.eyJ1c2VyX2lkIjoiYWJjIiwiZXhwIjoxNzAwMDAwMDAwfQ
.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

`.`으로 구분된 **세 부분**으로 이루어집니다.

| 부분 | 내용 | 비고 |
|------|------|------|
| 헤더 (Header) | `{"alg": "HS256", "typ": "JWT"}` | 알고리즘 정보 |
| 페이로드 (Payload) | `{"sub": "user-id", "exp": 1700000}` | 사용자 정보 + 만료 시간 |
| 서명 (Signature) | `HMAC(헤더 + 페이로드, 비밀키)` | 위변조 방지 |

---
### 페이로드는 Base64 인코딩 — 누구나 볼 수 있음

```python
import base64, json

payload = "eyJ1c2VyX2lkIjoiYWJjIiwiZXhwIjoxNzAwMDAwMDAwfQ"
decoded = base64.b64decode(payload + "==")
print(json.loads(decoded))
# {"user_id": "abc", "exp": 1700000000}
```

> **페이로드는 누구나 디코딩할 수 있습니다.**  
> 민감한 정보(비밀번호, 카드번호)는 절대 페이로드에 넣지 않습니다.

---
### 왜 안전한가 — 서명 검증

```
서버가 발급할 때:
  서명 = HMAC(헤더.페이로드, 서버만 아는 비밀키)

클라이언트가 토큰을 받아서 페이로드를 수정하면:
  수정된 토큰의 서명 ≠ 서버 검증 결과
  → "위변조된 토큰" → 401 거부

비밀키를 모르면 서명을 만들 수 없음
→ 페이로드를 바꾸면 서명이 맞지 않아 거부됨
```

---
## 2. access_token vs refresh_token

Supabase Auth 로그인은 두 가지 토큰을 반환합니다.

| 항목 | access_token | refresh_token |
|------|--------------|---------------|
| 용도 | API 요청 인증 | access_token 갱신 |
| 전달 방법 | `Authorization: Bearer {token}` 헤더 | 서버 내부에만 보관 |
| 만료 시간 | 짧음 (기본 1시간) | 김 (기본 7일) |
| 유출 시 | 1시간 후 자동 만료 | 즉시 무효화 조치 필요 |
| 저장 위치 | 메모리 또는 session | HttpOnly 쿠키 또는 서버 |

---
### 전체 프로세스 
```
로그인 → access_token (1시간) + refresh_token (7일)

1시간 후: access_token 만료
  ↓
refresh_token으로 새 access_token 발급 (재로그인 불필요)

7일 후: refresh_token 만료
  ↓
다시 이메일/비밀번호로 로그인
```

---
## 3. Supabase Auth 설정

---
### 이메일 인증 비활성화 (개발용)

Supabase Dashboard에서:
1. **Authentication** → **Providers** → **Email**
2. **"Confirm email"** 옵션을 **끄기** (OFF)
3. **Save** 클릭

이 설정을 끄면 회원가입 즉시 로그인할 수 있습니다.  
운영 환경에서는 반드시 켜야 합니다.

---
## 4. 회원가입 구현

```python
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client

def public_client():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.post("/auth/signup", status_code=201)
def signup(data: SignupRequest):
    try:
        result = public_client().auth.sign_up({
            "email": data.email,
            "password": data.password,
        })
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    ...
```

---
### EmailStr — 이메일 형식 자동 검증

```python
# pydantic[email] 설치 필요
# requirements.txt에 email-validator 포함

from pydantic import EmailStr

class SignupRequest(BaseModel):
    email: EmailStr  # "user@" → 422, "user@example.com" → 통과
```

---
## 5. 로그인 구현
> 응답에서 `access_token`을 복사해서 이후 요청에 사용합니다.
```python
@app.post("/auth/login")
def login(data: LoginRequest):
    try:
        result = public_client().auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })
    except Exception as exc:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다") from exc

    return {
        ...
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "token_type": "bearer",
    }
```

---
## 7. HTTPBearer — Bearer 토큰 받기

### 헤더 형식

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
> `Bearer ` 다음에 access_token을 붙입니다. (공백 포함, 대소문자 중요)

---
### FastAPI HTTPBearer 설정

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from pydantic import BaseModel

security = HTTPBearer()

class CurrentUser(BaseModel):
    id: str
    email: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    token = credentials.credentials  # "Bearer " 이후의 실제 토큰값

    try:
        result = public_client().auth.get_user(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from exc
...
```

---
### 보호된 엔드포인트

```python
@app.get("/me")
def get_me(current: CurrentUser = Depends(get_current_user)):
    return {
        "user_id": current.id,
        "email": current.email,
        "message": "인증 성공!"
    }
```

---
## 8. Swagger에서 Bearer 토큰 입력 방법

```
1. POST /auth/login 실행 → 응답에서 "access_token" 값 복사

2. Swagger UI 우측 상단 Authorize 버튼 클릭

3. Value 입력란에 입력:
   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   (앞에 "Bearer " 포함해서 입력!)

4. Authorize 버튼 클릭 → Close

5. 이후 모든 보호된 엔드포인트 요청에 자동으로 헤더가 추가됨
```

> **주의**: `Bearer ` (공백 포함)을 앞에 붙여야 합니다.  
> `eyJhbGci...`만 입력하면 401이 발생합니다.

---
## 9. Swagger에서 토큰 없이 요청하면

`HTTPBearer`가 설정된 엔드포인트에 토큰 없이 요청하면:

```json
// 401 Unauthorized
{
  "detail": "Not authenticated"
}
```

Swagger에서 자물쇠 아이콘이 닫혀 있으면 토큰이 설정된 상태입니다.

---
## 10.  실습 순서

1. Supabase Dashboard → Authentication → Email → "Confirm email" 끄기
2. `.env`에 `SUPABASE_ANON_KEY` 추가
3. `POST /auth/signup` → 사용자 A 가입
4. `POST /auth/login` → A로 로그인 → `access_token` 복사
5. Swagger → **Authorize** → `Bearer {토큰}` 입력
6. `GET /me` → 로그인한 사용자 정보 확인
7. 토큰 없이 `GET /me` → 401 확인
8. `POST /auth/signup` → 사용자 B 가입
9. B로 로그인 → 다른 `access_token` 확인
10. A 토큰으로 `GET /me` → A 정보, B 토큰으로 → B 정보 확인

---
## 핵심 패턴 요약

| 기능 | 코드 |
|------|------|
| 회원가입 | `auth.sign_up({"email": ..., "password": ...})` |
| 로그인 | `auth.sign_in_with_password({"email": ..., "password": ...})` |
| 토큰에서 사용자 | `auth.get_user(token)` |
| Bearer 의존성 | `security = HTTPBearer()` + `Depends(security)` |
| 현재 사용자 의존성 | `current: CurrentUser = Depends(get_current_user)` |
| 이메일 검증 | `email: EmailStr` |
| anon 클라이언트 | `create_client(URL, ANON_KEY)` |
