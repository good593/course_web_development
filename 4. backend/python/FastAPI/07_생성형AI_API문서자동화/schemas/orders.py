from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


# 주문 한 줄에 필요한 상품 ID와 수량입니다.
class OrderItemIn(BaseModel):
    product_id: int = Field(gt=0, description="주문할 상품 ID")
    quantity: int = Field(gt=0, description="주문 수량")


# 주문 생성 요청은 여러 개의 OrderItemIn을 리스트로 받습니다.
class OrderCreate(BaseModel):
    # Swagger UI에서 바로 실행해 볼 수 있는 주문 예시입니다.
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"items": [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 1}]}
            ]
        }
    )
    items: List[OrderItemIn] = Field(min_length=1, description="주문 상품 목록")


# 주문 생성/조회 API가 반환하는 응답 구조입니다.
class OrderResponse(BaseModel):
    id: int
    items: List[dict]
    total_price: int
    status: str
    created_at: datetime
