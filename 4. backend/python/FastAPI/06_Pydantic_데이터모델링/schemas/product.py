from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ProductStatus = Literal["active", "inactive", "sold_out"]


# 중첩 모델
class Category(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=50)
    slug: str = Field(pattern=r"^[a-z0-9-]+$", description="URL 친화적 식별자")


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=100, description="상품명")
    description: Optional[str] = Field(default=None, max_length=500)
    original_price: int = Field(gt=0, description="정가 (원)")
    sale_price: Optional[int] = Field(default=None, gt=0, description="할인가 (원)")
    stock: int = Field(default=0, ge=0)
    sku: str = Field(pattern=r"^[A-Z]{2}-\d{4}$", description="재고 관리 코드 (예: AB-1234)")
    status: ProductStatus = "active"
    tags: List[str] = Field(default_factory=list, max_length=10)


# 입력 스키마
class ProductCreate(ProductBase):
    category_id: int

    @field_validator("name")
    @classmethod
    def name_no_special_chars(cls, v: str) -> str:
        forbidden = ["<", ">", "&", '"', "'"]
        for char in forbidden:
            if char in v:
                raise ValueError(f"상품명에 '{char}' 문자는 사용할 수 없습니다.")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def tags_lowercase(cls, v: List[str]) -> List[str]:
        return [tag.lower().strip() for tag in v]

    @model_validator(mode="after")
    def sale_price_less_than_original(self) -> "ProductCreate":
        if self.sale_price is not None and self.sale_price >= self.original_price:
            raise ValueError("할인가는 정가보다 낮아야 합니다.")
        return self


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    sale_price: Optional[int] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    status: Optional[ProductStatus] = None


# 응답 스키마
class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: Optional[Category] = None
    discount_rate: Optional[float] = None
    created_at: datetime
