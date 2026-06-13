from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

app = FastAPI(title="POST 실습 API", version="0.1.0")

items_db: dict[int, dict] = {}
users_db: dict[int, dict] = {}
next_item_id = 1
next_user_id = 1


def fake_hash_password(password: str) -> str:
    """실습용 해시 함수입니다. 실제 서비스에서는 bcrypt 같은 검증된 해시를 사용하세요."""
    return f"fakehashed:{password}"


def verify_password(plain_password: str, password_hash: str) -> bool:
    return fake_hash_password(plain_password) == password_hash


# ── 아이템 스키마 ──────────────────────────────────

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


# ── 유저 스키마 ───────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="이름 (2~50자)")
    email: EmailStr = Field(description="이메일 주소")
    password: str = Field(min_length=8, description="비밀번호 (8자 이상)")
    age: Optional[int] = Field(default=None, ge=0, le=150, description="나이")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int]
    created_at: datetime


# ── 로그인 스키마 ─────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    message: str
    user_name: str
    email: str


# ── 아이템 엔드포인트 ─────────────────────────────

@app.post("/items", response_model=ItemResponse, status_code=201, tags=["items"])
def create_item(item: ItemCreate):
    """아이템 생성"""
    global next_item_id

    for existing in items_db.values():
        if existing["name"] == item.name:
            raise HTTPException(status_code=400, detail=f"'{item.name}' 이름의 아이템이 이미 존재합니다")

    new_item = {
        "id": next_item_id,
        **item.model_dump(),
        "created_at": datetime.now(),
    }
    items_db[next_item_id] = new_item
    next_item_id += 1
    return new_item


# ── 유저 엔드포인트 ───────────────────────────────

@app.post("/users", response_model=UserResponse, status_code=201, tags=["users"])
def create_user(user: UserCreate):
    """유저 등록"""
    global next_user_id

    for existing in users_db.values():
        if existing["email"] == user.email:
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")

    new_user = {
        "id": next_user_id,
        "name": user.name,
        "email": user.email,
        "password_hash": fake_hash_password(user.password),
        "age": user.age,
        "created_at": datetime.now(),
    }
    users_db[next_user_id] = new_user
    next_user_id += 1
    return new_user


@app.post("/login", response_model=LoginResponse, tags=["auth"])
def login(credentials: LoginRequest):
    """로그인"""
    found_user = next(
        (u for u in users_db.values() if u["email"] == credentials.email),
        None,
    )
    if not found_user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")
    if not verify_password(credentials.password, found_user["password_hash"]):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")

    return LoginResponse(
        message="로그인 성공",
        user_name=found_user["name"],
        email=found_user["email"],
    )
