from fastapi import APIRouter, HTTPException, Path

from models.shop import shop_db
from schemas.common import COMMON_ERRORS, ErrorResponse
from schemas.order import OrderCreate, OrderResponse

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=201,
    summary="주문 생성",
    description="상품을 주문합니다. 재고 확인 후 자동으로 재고가 차감됩니다.",
    responses={
        400: {"description": "재고 부족", "model": ErrorResponse},
        404: {"description": "상품을 찾을 수 없음", "model": ErrorResponse},
        **COMMON_ERRORS,
    },
)
def create_order(order: OrderCreate):
    for item in order.items:
        product = shop_db.get_product(item.product_id)
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

    return shop_db.create_order(order)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="주문 조회",
    responses={404: {"description": "주문을 찾을 수 없음", "model": ErrorResponse}},
)
def get_order(order_id: int = Path(description="조회할 주문 ID", ge=1)):
    order = shop_db.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    return order
