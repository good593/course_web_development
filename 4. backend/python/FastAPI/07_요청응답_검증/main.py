from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="요청·응답 검증 실습")


# ── 공통 에러 응답 형식 ───────────────────────────────────────────────────────

def error_response(code: str, message: str, details=None):
    body = {"success": False, "error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body


# ── 커스텀 예외 핸들러 ────────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field_path = ".".join(str(loc) for loc in err["loc"][1:])
        errors.append({
            "field": field_path,
            "message": err["msg"],
            "type": err["type"],
        })
    return JSONResponse(
        status_code=422,
        content=error_response("VALIDATION_ERROR", "입력값이 올바르지 않습니다.", errors),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response("HTTP_ERROR", str(exc.detail)),
    )


# ── Pydantic 스키마 ───────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30, description="영문/숫자/밑줄만 허용")
    email: EmailStr
    password: str = Field(min_length=8)
    password_confirm: str
    age: Optional[int] = Field(default=None, ge=0, le=150)
    role: str = Field(default="user")

    @field_validator("username")
    @classmethod
    def username_valid_chars(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("사용자명은 영문, 숫자, 밑줄(_)만 허용됩니다.")
        return v.lower()

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        return self


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=30)
    age: Optional[int] = Field(default=None, ge=0, le=150)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: Optional[int]
    role: str
    active: bool
    created_at: datetime


# ── 인메모리 DB ───────────────────────────────────────────────────────────────

users_db: dict[int, dict] = {
    1: {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": "hashed_pw",
        "age": 30,
        "role": "admin",
        "active": True,
        "created_at": datetime(2024, 1, 1),
    }
}
next_user_id = 2


# ── 엔드포인트 ────────────────────────────────────────────────────────────────

@app.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
def create_user(user: UserCreate):
    # 이메일 중복 체크
    if any(u["email"] == user.email for u in users_db.values()):
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")

    # 사용자명 중복 체크
    if any(u["username"] == user.username for u in users_db.values()):
        raise HTTPException(status_code=409, detail="이미 사용 중인 사용자명입니다.")

    global next_user_id
    new_user = {
        "id": next_user_id,
        "username": user.username,
        "email": user.email,
        "password_hash": f"hashed_{user.password}",
        "age": user.age,
        "role": user.role,
        "active": True,
        "created_at": datetime.now(),
    }
    users_db[next_user_id] = new_user
    next_user_id += 1
    return new_user


@app.get("/users", response_model=List[UserResponse], tags=["Users"])
def list_users():
    return list(users_db.values())


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user


@app.patch("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: int, update: UserUpdate):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if not user["active"]:
        raise HTTPException(status_code=403, detail="비활성화된 계정은 수정할 수 없습니다.")

    # 사용자명 중복 체크
    if update.username:
        conflict = next(
            (u for u in users_db.values() if u["username"] == update.username and u["id"] != user_id),
            None,
        )
        if conflict:
            raise HTTPException(status_code=409, detail="이미 사용 중인 사용자명입니다.")

    update_data = update.model_dump(exclude_none=True)
    user.update(update_data)
    return user


@app.delete("/users/{user_id}", status_code=204, tags=["Users"])
def delete_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    del users_db[user_id]


@app.post("/users/{user_id}/deactivate", response_model=UserResponse, tags=["Users"])
def deactivate_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if not user["active"]:
        raise HTTPException(status_code=400, detail="이미 비활성화된 계정입니다.")
    user["active"] = False
    return user


# ── 주문 상태 전이 예제 ───────────────────────────────────────────────────────

ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["processing", "cancelled"],
    "processing": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": [],
    "cancelled": [],
}

orders_db: dict[int, dict] = {
    1: {"id": 1, "status": "pending", "user_id": 1, "total": 50000},
    2: {"id": 2, "status": "shipped", "user_id": 1, "total": 120000},
}


class OrderStatusUpdate(BaseModel):
    status: str


@app.patch("/orders/{order_id}/status", tags=["Orders"])
def update_order_status(order_id: int, body: OrderStatusUpdate):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")

    current = order["status"]
    new_status = body.status

    if new_status not in ALLOWED_TRANSITIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_STATUS",
                "message": f"'{new_status}'는 유효한 주문 상태가 아닙니다.",
                "allowed": list(ALLOWED_TRANSITIONS.keys()),
            },
        )

    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_TRANSITION",
                "message": f"'{current}' 상태에서 '{new_status}'로 변경할 수 없습니다.",
                "current_status": current,
                "allowed_next": ALLOWED_TRANSITIONS[current],
            },
        )

    order["status"] = new_status
    return order
