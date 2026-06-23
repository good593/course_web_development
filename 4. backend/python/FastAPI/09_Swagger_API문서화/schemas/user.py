from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"username": "hong123", "email": "hong@example.com", "password": "pass1234"}]
        }
    )
    username: str = Field(min_length=3, max_length=30, description="사용자명 (3~30자)")
    email: str = Field(description="이메일 주소")
    password: str = Field(min_length=8, description="비밀번호 (8자 이상)")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
