from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"name": "무선 마우스", "price": 35000, "stock": 50, "category": "전자제품"},
                {"name": "면 티셔츠", "price": 19900, "stock": 200, "category": "의류"},
            ]
        }
    )

    name: str = Field(min_length=2, max_length=100, description="상품명 (2~100자)")
    price: int = Field(gt=0, description="판매가 (원, 0 초과)")
    stock: int = Field(ge=0, default=0, description="재고 수량")
    category: str = Field(description="카테고리명")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100, description="변경할 상품명")
    price: Optional[int] = Field(default=None, gt=0, description="변경할 판매가")
    stock: Optional[int] = Field(default=None, ge=0, description="변경할 재고 수량")


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    stock: int
    category: str
    created_at: datetime
