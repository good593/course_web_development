from fastapi import APIRouter, HTTPException

from models.product import product_db
from schemas.product import ProductCreate, ProductResponse, ProductStatus, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate):
    if not product_db.has_category(product.category_id):
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")

    if product_db.sku_exists(product.sku):
        raise HTTPException(status_code=409, detail=f"SKU '{product.sku}'는 이미 사용 중입니다.")

    new_product = product_db.create(product.model_dump())
    return product_db.build_response(new_product)


@router.get("", response_model=list[ProductResponse])
def list_products(
    status: ProductStatus | None = None,
    category_id: int | None = None,
):
    products = product_db.get_all(status=status, category_id=category_id)
    return [product_db.build_response(product) for product in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    product = product_db.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    return product_db.build_response(product)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, update: ProductUpdate):
    product = product_db.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    update_data = update.model_dump(exclude_none=True)

    new_sale = update_data.get("sale_price", product.get("sale_price"))
    original = product["original_price"]
    if new_sale is not None and new_sale >= original:
        raise HTTPException(status_code=400, detail="할인가는 정가보다 낮아야 합니다.")

    updated_product = product_db.update(product_id, update_data)
    return product_db.build_response(updated_product)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int):
    if not product_db.delete(product_id):
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
