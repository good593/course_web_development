from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# 요청 본문에 들어오는 상품 등록 데이터를 검증하는 스키마입니다.
class ProductCreate(BaseModel):
    # examples는 Swagger UI의 Example Value에 표시되어 학생들이 바로 테스트할 수 있습니다.
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


# 모든 필드가 Optional이면 PATCH 요청에서 바꾸고 싶은 값만 보낼 수 있습니다.
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100, description="변경할 상품명")
    price: Optional[int] = Field(default=None, gt=0, description="변경할 판매가")
    stock: Optional[int] = Field(default=None, ge=0, description="변경할 재고 수량")


# 응답 스키마는 클라이언트에게 어떤 필드가 돌아가는지 문서화합니다.
class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    stock: int
    category: str
    created_at: datetime
