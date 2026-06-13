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
# 프로젝트 구조화 & 종합 실습

---
## 1. APIRouter — 엔드포인트 분리

---
### 왜 분리하는가?

```python
# main.py가 커질수록 관리가 힘들어짐
app = FastAPI()

@app.get("/users")
@app.get("/users/{id}")
@app.post("/users")
@app.get("/items")
@app.get("/items/{id}")
@app.post("/items")
@app.get("/orders")
# ... 수십 개의 엔드포인트가 한 파일에
```

---
### APIRouter로 분리

```python
# routers/item.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/items",       # 모든 경로에 /items 자동 추가
    tags=["items"],        # Swagger UI 그룹 이름
)

@router.get("")            # → /items
def get_items(): ...

@router.get("/{item_id}") # → /items/{item_id}
def get_item(item_id: int): ...

@router.post("")           # → /items
def create_item(): ...
```

---
> routers 코드 import

```python
# main.py
from fastapi import FastAPI
from routers import item, user

app = FastAPI()

app.include_router(item.router)
app.include_router(user.router)
```

---
## 2. 의존성 주입 (Dependency Injection) 맛보기

---
### 공통 Query Parameter 재사용

```python
from fastapi import Depends

# 공통 페이지네이션 파라미터
def pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@app.get("/items")
def get_items(page: dict = Depends(pagination)):
    # page = {"skip": 0, "limit": 10}
    ...

@app.get("/users")
def get_users(page: dict = Depends(pagination)):
    # 같은 파라미터를 중복 정의하지 않아도 됨
    ...
```

---
### 간단한 인증 헤더 검사

```python
from fastapi import Depends, HTTPException, Header
from typing import Optional

def verify_token(x_token: Optional[str] = Header(default=None)):
    if x_token != "secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return x_token


# 특정 엔드포인트에만 인증 적용
@app.post("/admin/items", dependencies=[Depends(verify_token)])
def admin_create_item(item: ItemCreate):
    ...
```

---
## 3. 종합 실습 — Todo API 완성

---
### 프로젝트 구조

```
todo_api/
├── main.py
├── routers/
│   └── todo.py
├── models/
│   └── todo.py
└── schemas/
    └── todo.py
```

---
### 3-1. 스키마 정의

```python
# schemas/todo.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="할 일 제목")
    description: Optional[str] = Field(default=None, max_length=1000, description="상세 설명")
    priority: int = Field(default=2, ge=1, le=3, description="우선순위 (1=높음, 2=보통, 3=낮음)")

...
```

---
### 3-2. 데이터 모델 (인메모리)

```python
# models/todo.py

from datetime import datetime


class TodoDB:
    def __init__(self):
        self._data: dict[int, dict] = {}
        self._next_id = 1

    def create(self, title: str, description: str | None, priority: int) -> dict:
        todo = {
            "id": self._next_id,
            "title": title,
            "description": description,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now(),
        }
        self._data[self._next_id] = todo
        self._next_id += 1
        return todo

...
```

---
### 3-3. 라우터 구현

```python
# routers/todo.py

from fastapi import APIRouter, HTTPException
from schemas.todo import TodoCreate, TodoResponse, TodoListResponse
from models.todo import todo_db

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


@router.get("", response_model=TodoListResponse)
def get_todos(skip: int = 0, limit: int = 10):
    """할 일 목록 조회 (페이지네이션)"""
    return TodoListResponse(
        total=todo_db.count(),
        items=todo_db.get_all(skip=skip, limit=limit),
    )

...
```

---
### 3-4. 메인 앱

```python
# main.py

from fastapi import FastAPI
from routers.todo import router as todo_router

app = FastAPI(
    title="Todo API",
    description="FastAPI 입문 강의 종합 실습 프로젝트",
    version="1.0.0",
)

app.include_router(todo_router)


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Todo API에 오신 것을 환영합니다!", "docs": "/docs"}
```

---
## 4. API 동작 확인

---
### Swagger UI에서 순서대로 테스트

```
1. POST /todos  (할 일 3개 생성)
   {"title": "FastAPI 공부", "priority": 1}
   {"title": "운동하기", "description": "30분 달리기", "priority": 2}
   {"title": "책 읽기", "priority": 3}

2. GET /todos   (목록 확인)
   → total: 3, items: [...]

3. GET /todos/1  (단건 조회)
   → 첫 번째 할 일 반환

4. GET /todos/99  (없는 ID)
   → 404 Not Found

5. POST /todos  (검증 실패)
   {"title": ""}
   → 422 Unprocessable Entity

6. GET /todos?limit=2  (페이지네이션)
   → 2개만 반환
```

---
## 5. 전체 프로젝트 파일 트리

```
todo_api/
├── main.py
├── routers/
│   ├── __init__.py
│   └── todo.py
├── models/
│   ├── __init__.py
│   └── todo.py
└── schemas/
    ├── __init__.py
    └── todo.py
```

---
각 레이어의 역할:

| 레이어 | 파일 | 역할 |
|--------|------|------|
| 진입점 | `main.py` | 앱 생성, 라우터 등록 |
| 라우터 | `routers/todo.py` | HTTP 엔드포인트 정의 |
| 스키마 | `schemas/todo.py` | 입출력 데이터 구조 |
| 모델 | `models/todo.py` | 데이터 저장/조회 로직 |

---
## 6. 핵심 요약

| 개념 | 설명 |
|------|------|
| `APIRouter` | 엔드포인트를 모듈별로 분리 |
| `prefix` | 라우터 내 모든 경로에 공통 접두사 추가 |
| `tags` | Swagger UI 그룹화 |
| `include_router` | 메인 앱에 라우터 등록 |
| `Depends` | 공통 로직 재사용 (의존성 주입) |
