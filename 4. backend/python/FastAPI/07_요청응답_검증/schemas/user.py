from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


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
