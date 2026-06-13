from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime

app = FastAPI(title="Pydantic 데이터 모델링 실습")

# ── 중첩 모델 ────────────────────────────────────────────────────────────────

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
    status: Literal["active", "inactive", "sold_out"] = "active"
    tags: List[str] = Field(default_factory=list, max_length=10)


# ── 입력 스키마 ───────────────────────────────────────────────────────────────

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
    status: Optional[Literal["active", "inactive", "sold_out"]] = None


# ── 응답 스키마 ───────────────────────────────────────────────────────────────

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: Optional[Category] = None
    discount_rate: Optional[float] = None  # 계산된 필드
    created_at: datetime


# ── 인메모리 DB ───────────────────────────────────────────────────────────────

categories_db: dict[int, dict] = {
    1: {"id": 1, "name": "전자제품", "slug": "electronics"},
    2: {"id": 2, "name": "의류", "slug": "clothing"},
    3: {"id": 3, "name": "식품", "slug": "food"},
}

products_db: dict[int, dict] = {}
next_product_id = 1


def compute_discount_rate(original: int, sale: Optional[int]) -> Optional[float]:
    if sale is None:
        return None
    return round((1 - sale / original) * 100, 1)


def build_product_response(product: dict) -> dict:
    category_data = categories_db.get(product.get("category_id"))
    return {
        **product,
        "category": category_data,
        "discount_rate": compute_discount_rate(product["original_price"], product.get("sale_price")),
    }


# ── 카테고리 엔드포인트 ────────────────────────────────────────────────────────

@app.get("/categories", response_model=List[Category], tags=["Categories"])
def list_categories():
    return list(categories_db.values())


# ── 상품 엔드포인트 ───────────────────────────────────────────────────────────

@app.post("/products", response_model=ProductResponse, status_code=201, tags=["Products"])
def create_product(product: ProductCreate):
    global next_product_id

    if product.category_id not in categories_db:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")

    # SKU 중복 체크
    if any(p["sku"] == product.sku for p in products_db.values()):
        raise HTTPException(status_code=409, detail=f"SKU '{product.sku}'는 이미 사용 중입니다.")

    new_product = {
        "id": next_product_id,
        **product.model_dump(),
        "created_at": datetime.now(),
    }
    products_db[next_product_id] = new_product
    next_product_id += 1

    return build_product_response(new_product)


@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def list_products(
    status: Optional[Literal["active", "inactive", "sold_out"]] = None,
    category_id: Optional[int] = None,
):
    result = list(products_db.values())

    if status:
        result = [p for p in result if p["status"] == status]
    if category_id:
        result = [p for p in result if p.get("category_id") == category_id]

    return [build_product_response(p) for p in result]


@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: int):
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return build_product_response(product)


@app.patch("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def update_product(product_id: int, update: ProductUpdate):
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    update_data = update.model_dump(exclude_none=True)

    # 할인가 교차 검증
    new_sale = update_data.get("sale_price", product.get("sale_price"))
    original = product["original_price"]
    if new_sale is not None and new_sale >= original:
        raise HTTPException(status_code=400, detail="할인가는 정가보다 낮아야 합니다.")

    product.update(update_data)
    return build_product_response(product)


@app.delete("/products/{product_id}", status_code=204, tags=["Products"])
def delete_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    del products_db[product_id]
