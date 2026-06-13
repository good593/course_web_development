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
# GET 엔드포인트 구현

---

## 1. Path Parameter vs Query Parameter

> Path Parameter와 Query Parameter를 FastAPI 코드로 어떻게 받는지 구현합니다.

---
### Path Parameter — 특정 리소스 식별

```python
@app.get("/items/{item_id}")
#              ↑↑↑↑↑↑↑
#         Path Parameter
def get_item(item_id: int):
    return {"item_id": item_id}
```

```
GET /items/42      → item_id = 42
GET /items/100     → item_id = 100
GET /items/abc     → 422 Error (int 타입 불일치)
```

---
### Query Parameter — 필터 / 옵션

```python
@app.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    #          ↑↑↑↑             ↑↑↑↑↑
    #      Query Parameter   (기본값 있음)
    return {"skip": skip, "limit": limit}
```

```
GET /items              → skip=0, limit=10 (기본값)
GET /items?skip=20      → skip=20, limit=10
GET /items?skip=0&limit=5 → skip=0, limit=5
```

---
### 언제 무엇을 쓰나?

| 상황 | 사용 |
|------|------|
| 특정 유저 조회 `/users/42` | Path Parameter |
| 유저 목록 페이지 `/users?page=2` | Query Parameter |
| 특정 게시글 `/posts/10` | Path Parameter |
| 카테고리 필터 `/posts?category=tech` | Query Parameter |

---
## 2. 타입 힌트 기초
> FastAPI는 **Python 타입 힌트**를 읽어 자동으로 검증/문서화한다.

```python
from typing import Optional

@app.get("/items/{item_id}")
def get_item(
    item_id: int,                    # int만 허용
    q: Optional[str] = None,        # 선택적 문자열
    active: bool = True,            # 불리언 기본값
):
    return {
        "item_id": item_id,
        "q": q,
        "active": active,
    }
```

---
| 타입 | 허용값 예시 |
|------|------------|
| `int` | `1`, `42`, `100` |
| `float` | `3.14`, `1.0` |
| `str` | `"hello"`, `"world"` |
| `bool` | `true`, `false`, `1`, `0`, `on`, `off` |
| `Optional[str]` | `"hello"` 또는 `None` |

---
## 3. 응답 모델 (Response Model)
- [Pydantic](https://pydantic.dev/docs/validation/latest/get-started/)
    - Pydantic(파이댄틱)은 파이썬(Python) 타입 힌트를 활용하여 데이터 유효성 검사(Validation) 와 설정 관리(Settings Management) 를 수행하는 핵심 라이브러리입니다.
    - 개발자가 정의한 데이터 구조와 타입에 맞춰 외부의 불완전한 데이터를 검증하고, 파이썬 객체로 안전하게 변환(파싱)해 주는 역할을 합니다.

---
### 왜 필요한가?

```python
from pydantic import BaseModel

# 응답 모델 없이 반환하면 모든 필드가 노출됨
class User(BaseModel):
    id: int
    name: str
    email: str
    password: str   # ← 절대 노출되면 안 됨!

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": 1, "name": "홍길동", "email": "hong@ex.com", "password": "secret"}
    # password가 그대로 응답에 포함됨!!
```

---
### response_model로 응답 필드 제한

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str   # 입력 시 필요

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    # password 없음! ← 응답에서 제외

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    # password가 있어도 응답 모델이 걸러줌
    return {"id": 1, "name": "홍길동", "email": "hong@ex.com", "password": "secret"}
```

---
## 4. 실습 — GET 엔드포인트 3종 구현

---
### 4-1. 데이터 준비 (인메모리)

```python
# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Item API", version="0.1.0")

# 임시 데이터베이스 (딕셔너리)
fake_db: dict[int, dict] = {
    1: {"id": 1, "name": "노트북", "price": 1500000, "category": "전자기기", "in_stock": True},
    2: {"id": 2, "name": "마우스", "price": 35000,   "category": "전자기기", "in_stock": True},
    3: {"id": 3, "name": "책상",   "price": 250000,  "category": "가구",     "in_stock": False},
    4: {"id": 4, "name": "의자",   "price": 180000,  "category": "가구",     "in_stock": True},
}
```

---
### 4-2. 응답 스키마 정의

```python
class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str
    in_stock: bool
```

---
### 4-3. 목록 조회 (Query Parameter)

```python
@app.get("/items", response_model=List[ItemResponse])
def get_items(skip: int = 0, limit: int = 10):
    """
    아이템 목록 조회

    - **skip**: 건너뛸 개수 (기본값: 0)
    - **limit**: 최대 반환 개수 (기본값: 10)
    """
    items = list(fake_db.values())
    return items[skip : skip + limit]
```

```
GET /items           → 전체 목록 (최대 10개)
GET /items?skip=2    → 2개 건너뛰고 반환
GET /items?limit=2   → 최대 2개만 반환
```

---
### 4-4. 단건 조회 (Path Parameter)

```python
@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    """특정 아이템 단건 조회"""
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return fake_db[item_id]
```

```
GET /items/1    → 노트북 반환
GET /items/99   → 404 Not Found
GET /items/abc  → 422 Unprocessable Entity (타입 오류)
```

---
### 4-5. 검색 (Query Parameter 다중)

```python
@app.get("/items/search", response_model=List[ItemResponse])
def search_items(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    in_stock: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    """
    아이템 검색

    - **keyword**: 이름에 포함된 키워드
    - **category**: 카테고리 필터
    - **in_stock**: 재고 여부 필터
    - **min_price**: 최소 가격
    - **max_price**: 최대 가격
    """
    results = list(fake_db.values())

    if keyword:
        results = [i for i in results if keyword in i["name"]]
    if category:
        results = [i for i in results if i["category"] == category]
    if in_stock is not None:
        results = [i for i in results if i["in_stock"] == in_stock]
    if min_price is not None:
        results = [i for i in results if i["price"] >= min_price]
    if max_price is not None:
        results = [i for i in results if i["price"] <= max_price]

    return results
```

---
> **주의** : `/items/search`와 `/items/{item_id}`가 충돌할 수 있다.
> FastAPI는 **위에서 아래로** 경로를 매칭하므로 `/items/search`를 **먼저** 정의해야 한다.

```python
# 올바른 순서
@app.get("/items/search")   # 먼저 정의
def search_items(...): ...

@app.get("/items/{item_id}")  # 나중에 정의
def get_item(item_id: int): ...

# 잘못된 순서 → search가 item_id로 잡힘
@app.get("/items/{item_id}")
@app.get("/items/search")
```

---
## 5. 핵심 요약

| 개념 | 사용법 |
|------|--------|
| Path Parameter | `@app.get("/items/{id}")` + 함수 인자 |
| Query Parameter | 기본값 있는 함수 인자 |
| 404 반환 | `raise HTTPException(status_code=404, ...)` |
| 응답 모델 | `@app.get(..., response_model=Model)` |
| 경로 우선순위 | 고정 경로(`/search`)를 변수 경로(`/{id}`)보다 먼저 선언 |
