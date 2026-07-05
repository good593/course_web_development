from datetime import datetime

from fastapi import HTTPException

from schemas.orders import OrderCreate
from schemas.products import ProductCreate, ProductUpdate
from schemas.users import UserCreate

# 수업에서는 DB 설정을 줄이기 위해 딕셔너리를 임시 저장소로 사용합니다.
# 서버를 재시작하면 아래 데이터는 처음 상태로 돌아갑니다.
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

# 실제 DB의 AUTO_INCREMENT처럼 새 데이터의 ID를 하나씩 증가시키는 값입니다.
_next_ids = {"product": 3, "order": 1, "user": 1}


def list_products(category: str | None = None, page: int = 1, size: int = 10) -> list[dict]:
    """카테고리 필터와 페이지네이션을 적용해 상품 목록을 반환합니다."""
    items = list(products_db.values())
    if category:
        items = [product for product in items if product["category"] == category]

    # page=1이면 0번부터, page=2이면 size만큼 건너뛴 위치부터 잘라 냅니다.
    start = (page - 1) * size
    return items[start: start + size]


def create_product(product: ProductCreate) -> dict:
    """상품명을 중복 검사한 뒤 새 상품을 저장합니다."""
    if any(saved["name"] == product.name for saved in products_db.values()):
        raise HTTPException(status_code=409, detail="동일한 상품명이 이미 존재합니다.")

    product_id = _next_ids["product"]
    _next_ids["product"] += 1
    new_product = {"id": product_id, **product.model_dump(), "created_at": datetime.now()}
    products_db[product_id] = new_product
    return new_product


def get_product(product_id: int) -> dict:
    """ID로 상품을 찾고, 없으면 404 오류를 발생시킵니다."""
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return product


def update_product(product_id: int, update: ProductUpdate) -> dict:
    """PATCH 요청에서 전달된 필드만 기존 상품에 덮어씁니다."""
    product = get_product(product_id)
    product.update(update.model_dump(exclude_none=True))
    return product


def delete_product(product_id: int) -> None:
    """상품을 삭제하고, 없는 상품이면 404 오류를 발생시킵니다."""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    del products_db[product_id]


def create_order(order: OrderCreate) -> dict:
    """주문 상품의 존재 여부와 재고를 확인한 뒤 주문을 생성합니다."""
    items_detail = []
    total_price = 0

    # 먼저 모든 상품을 검증해서, 중간에 실패했을 때 재고가 일부만 줄어드는 일을 막습니다.
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

    # 검증이 끝난 뒤에 실제 재고를 차감합니다.
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
    """ID로 주문을 찾고, 없으면 404 오류를 발생시킵니다."""
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    return order


def create_user(user: UserCreate) -> dict:
    """이메일 중복을 검사한 뒤 새 사용자를 저장합니다."""
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
    """인증 예제에서 사용할 고정 데모 사용자를 반환합니다."""
    return {
        "id": 1,
        "username": "demo_user",
        "email": "demo@example.com",
        "created_at": datetime.now(),
    }
