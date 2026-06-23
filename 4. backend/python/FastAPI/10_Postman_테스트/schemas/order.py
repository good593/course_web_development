from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class OrderItemIn(BaseModel):
    product_id: int = Field(gt=0, description="주문할 상품 ID")
    quantity: int = Field(gt=0, description="주문 수량")


class OrderCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"items": [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 1}]}
            ]
        }
    )
    items: List[OrderItemIn] = Field(min_length=1, description="주문 상품 목록")


class OrderResponse(BaseModel):
    id: int
    items: List[dict]
    total_price: int
    status: str
    created_at: datetime
