from datetime import datetime

from fastapi import HTTPException

from schemas.orders import OrderCreate
from schemas.products import ProductCreate, ProductUpdate
from schemas.users import UserCreate

products_db: dict[int, dict] = {
    1: {
        "id": 1,
        "name": "무선 마우스",
        "price": 35000,
        "stock": 50,
        "category": "전자제품",
        "created_at": datetime(2024, 1, 10),
    },
    2: {
        "id": 2,
        "name": "기계식 키보드",
        "price": 89000,
        "stock": 20,
        "category": "전자제품",
        "created_at": datetime(2024, 1, 15),
    },
}
orders_db: dict[int, dict] = {}
users_db: dict[int, dict] = {}
_next_ids = {"product": 3, "order": 1, "user": 1}


def list_products(category: str | None = None, page: int = 1, size: int = 10) -> list[dict]:
    items = list(products_db.values())
    if category:
        items = [product for product in items if product["category"] == category]

    start = (page - 1) * size
    return items[start: start + size]


def create_product(product: ProductCreate) -> dict:
    if any(saved["name"] == product.name for saved in products_db.values()):
        raise HTTPException(status_code=409, detail="동일한 상품명이 이미 존재합니다.")

    product_id = _next_ids["product"]
    _next_ids["product"] += 1
    new_product = {"id": product_id, **product.model_dump(), "created_at": datetime.now()}
    products_db[product_id] = new_product
    return new_product


def get_product(product_id: int) -> dict:
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return product


def update_product(product_id: int, update: ProductUpdate) -> dict:
    product = get_product(product_id)
    product.update(update.model_dump(exclude_none=True))
    return product


def delete_product(product_id: int) -> None:
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    del products_db[product_id]


def create_order(order: OrderCreate) -> dict:
    items_detail = []
    total_price = 0

    for item in order.items:
        product = products_db.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"상품 ID {item.product_id}를 찾을 수 없습니다.")
        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INSUFFICIENT_STOCK",
                    "product_id": item.product_id,
                    "available": product["stock"],
                    "requested": item.quantity,
                },
            )

        total_price += product["price"] * item.quantity
        items_detail.append(
            {
                "product_id": item.product_id,
                "name": product["name"],
                "quantity": item.quantity,
                "unit_price": product["price"],
            }
        )

    for item in order.items:
        products_db[item.product_id]["stock"] -= item.quantity

    order_id = _next_ids["order"]
    _next_ids["order"] += 1
    new_order = {
        "id": order_id,
        "items": items_detail,
        "total_price": total_price,
        "status": "pending",
        "created_at": datetime.now(),
    }
    orders_db[order_id] = new_order
    return new_order


def get_order(order_id: int) -> dict:
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    return order


def create_user(user: UserCreate) -> dict:
    if any(saved["email"] == user.email for saved in users_db.values()):
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")

    user_id = _next_ids["user"]
    _next_ids["user"] += 1
    new_user = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "created_at": datetime.now(),
    }
    users_db[user_id] = new_user
    return new_user


def get_demo_user() -> dict:
    return {
        "id": 1,
        "username": "demo_user",
        "email": "demo@example.com",
        "created_at": datetime.now(),
    }
