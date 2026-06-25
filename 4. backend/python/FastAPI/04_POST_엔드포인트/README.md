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
# POST 엔드포인트 구현
- 데이터를 **Request Body에 포함**
- **생성 / 처리** 목적
- URL에 데이터가 노출되지 않음
- 데이터 크기 제한 없음
- 민감한 정보 전송 가능

---
## GET vs POST

| 항목 | GET | POST |
|------|-----|------|
| 데이터 위치 | URL Query String | Request Body |
| 데이터 크기 | 제한 있음 | 제한 없음 |
| 보안 | URL에 노출 | Body에 숨김 |
| 캐싱 | 가능 | 불가 |
| 목적 | 조회 | 생성/처리 |

---
## 1. Request Body와 Pydantic BaseModel

> POST는 데이터를 URL이 아닌 Body에 담습니다.
> FastAPI에서는 Pydantic BaseModel이 이 Body를 자동으로 받아 검증합니다.

```shell
POST /items HTTP/1.1
Content-Type: application/json

{
    "name": "키보드",
    "price": 89000,
    "category": "전자기기"
}
```

---
### BaseModel로 Body 스키마 정의

```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float
    category: str
    in_stock: bool = True   # 기본값 있는 선택 필드
```

---
```python
@app.post("/items")
def create_item(item: ItemCreate):
    #            ↑↑↑↑
    #   Body 데이터 자동 파싱 + 검증
    return item
```

FastAPI가 자동으로 처리하는 것:
- JSON → Python 객체 변환
- 타입 검증 (price에 문자열이 오면 422 반환)
- 필수 필드 누락 시 422 반환
- Swagger UI에 Body 스키마 자동 문서화

---
## 2. Field로 유효성 규칙 추가

---
### 기본 Field 사용법

```python
from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="아이템 이름",
        examples=["노트북"],
    )
    price: float = Field(
        gt=0,                     # greater than 0 (0 초과)
        description="가격 (0보다 커야 함)",
        examples=[15000],
    )
    category: str = Field(
        description="카테고리",
        examples=["전자기기"],
    )
    in_stock: bool = Field(
        default=True,
        description="재고 여부",
    )
```

---
### 주요 Field 검증 옵션

| 옵션 | 적용 타입 | 의미 |
|------|----------|------|
| `min_length` | str | 최소 길이 |
| `max_length` | str | 최대 길이 |
| `pattern` | str | 정규표현식 패턴 |
| `gt` | int/float | 초과 (greater than) |
| `ge` | int/float | 이상 (greater or equal) |
| `lt` | int/float | 미만 (less than) |
| `le` | int/float | 이하 (less or equal) |
| `default` | 모든 타입 | 기본값 |

---
### 이메일 검증
```python
from pydantic import BaseModel, EmailStr

# pip install pydantic[email] 필요
class UserCreate(BaseModel):
    name: str
    email: EmailStr   # 이메일 형식 자동 검증
    password: str = Field(min_length=8)
```

---
## 3. 입력/출력 스키마 분리

입력(요청)과 출력(응답)에 필요한 필드가 다른 경우 스키마를 분리한다.

```python
# 입력 스키마 (클라이언트 → 서버)
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    category: str
    in_stock: bool = True

# 출력 스키마 (서버 → 클라이언트)
class ItemResponse(BaseModel):
    id: int              # 서버가 생성
    name: str
    price: float
    category: str
    in_stock: bool
    created_at: datetime  # 서버가 생성
```

---
## 4. 실습 — POST 엔드포인트 3종 구현

---
### 4-1. 아이템 생성 API

```python
app = FastAPI(title="POST 실습 API")

# 인메모리 저장소
items_db: dict[int, dict] = {}
next_id = 1

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="아이템 이름")
    price: float = Field(gt=0, description="가격 (0 초과)")
    category: str = Field(min_length=1, description="카테고리")
    in_stock: bool = Field(default=True, description="재고 여부")

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str
    in_stock: bool
    created_at: datetime

@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate):
    """아이템 생성"""
    global next_id

    # 중복 이름 체크
    for existing in items_db.values():
        if existing["name"] == item.name:
            raise HTTPException(status_code=400, detail=f"'{item.name}' 이름의 아이템이 이미 존재합니다")

...
```

---
```
# 성공
POST /items
{"name": "키보드", "price": 89000, "category": "전자기기"}
→ 201 Created

# 실패: 가격 0 이하
POST /items
{"name": "마우스", "price": -100, "category": "전자기기"}
→ 422 Unprocessable Entity

# 실패: 중복 이름
POST /items (키보드 두 번째)
→ 400 Bad Request
```

---
### 4-2. 유저 등록 API (이메일 검증)

```python
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    """유저 등록"""
    global next_user_id

    # 이메일 중복 체크
    for existing in users_db.values():
        if existing["email"] == user.email:
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")

    new_user = {
        "id": next_user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "password_hash": fake_hash_password(user.password),
        # password 원문은 저장하지 않고 응답 모델에서도 제외됨
        "created_at": datetime.now(),
    }
    users_db[next_user_id] = new_user
    next_user_id += 1

    return new_user
```

---
```
# 성공
POST /users
{"name": "홍길동", "email": "hong@example.com", "password": "pass1234"}
→ 201 Created (password 없는 응답)

# 실패: 잘못된 이메일
POST /users
{"name": "홍길동", "email": "not-an-email", "password": "pass1234"}
→ 422 Unprocessable Entity

# 실패: 비밀번호 너무 짧음
POST /users
{"name": "홍길동", "email": "hong@example.com", "password": "123"}
→ 422 Unprocessable Entity
```

---
### 4-3. 로그인 API (입력값 검증)

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    message: str
    user_name: str
    email: str


@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    """로그인 (간단한 예시 — 실제 환경에서는 JWT 사용)"""

    # 유저 찾기
    found_user = None
    for user in users_db.values():
        if user["email"] == credentials.email:
            found_user = user
            break

    if not found_user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")

    if not verify_password(credentials.password, found_user["password_hash"]):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")

    return LoginResponse(
        message="로그인 성공",
        user_name=found_user["name"],
        email=found_user["email"],
    )
```

---
## 5. 422 에러 응답 분석

```json
{
    "detail": [
        {
            "type": "missing",
            "loc": ["body", "name"],
            "msg": "Field required",
            "input": {"price": 100}
        },
        ...
    ]
}
```
- `loc` : 오류 위치 (`body` → `필드명`)
- `type` : 오류 종류
- `msg` : 오류 메시지

---

## 6. 핵심 요약

| 개념 | 사용법 |
|------|--------|
| Request Body | `BaseModel`을 함수 인자 타입으로 지정 |
| 필드 검증 | `Field(gt=0, min_length=1, ...)` |
| 이메일 검증 | `EmailStr` (pydantic[email] 필요) |
| 201 응답 | `@app.post(..., status_code=201)` |
| 응답에서 필드 제외 | 입력/출력 스키마 분리 |
| 비즈니스 로직 오류 | `raise HTTPException(status_code=400, ...)` |
