from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# 회원 가입 요청 본문을 검증하는 스키마입니다.
class UserCreate(BaseModel):
    # 수업에서는 이 예시가 Swagger UI의 Example Value로 보입니다.
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"username": "hong123", "email": "hong@example.com", "password": "pass1234"}]
        }
    )
    username: str = Field(min_length=3, max_length=30, description="사용자명 (3~30자)")
    email: str = Field(description="이메일 주소")
    password: str = Field(min_length=8, description="비밀번호 (8자 이상)")


# 비밀번호는 응답에 포함하지 않는 것이 기본 보안 원칙입니다.
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
