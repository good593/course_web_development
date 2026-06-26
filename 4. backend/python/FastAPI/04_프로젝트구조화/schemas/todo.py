from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="할 일 제목")
    description: Optional[str] = Field(default=None, max_length=1000, description="상세 설명")
    priority: int = Field(default=2, ge=1, le=3, description="우선순위 (1=높음, 2=보통, 3=낮음)")


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: int
    completed: bool
    created_at: datetime


class TodoListResponse(BaseModel):
    total: int
    items: list[TodoResponse]
