from datetime import datetime

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, examples=["FastAPI와 SQLite로 CRUD 만들기"])
    content: str = Field(..., min_length=1, examples=["sqlite3 표준 라이브러리로 게시글을 저장합니다."])
    summary: str | None = Field(default=None, max_length=500, examples=["SQLite 기반 CRUD 실습"])
    published: bool = Field(default=False, description="공개 여부")


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    summary: str | None = Field(default=None, max_length=500)
    published: bool | None = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str | None
    published: bool
    created_at: datetime
    updated_at: datetime


class PaginatedPosts(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[PostResponse]
