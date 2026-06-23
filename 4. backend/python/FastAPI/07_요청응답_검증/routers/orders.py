from fastapi import APIRouter, HTTPException

from models.order import order_db
from schemas.order import OrderStatusUpdate

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.patch("/{order_id}/status")
def update_order_status(order_id: int, body: OrderStatusUpdate):
    order = order_db.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")

    current = order["status"]
    new_status = body.status

    if new_status not in order_db.allowed_statuses():
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_STATUS",
                "message": f"'{new_status}'는 유효한 주문 상태가 아닙니다.",
                "allowed": order_db.allowed_statuses(),
            },
        )

    allowed_next = order_db.allowed_next_statuses(current)
    if new_status not in allowed_next:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_TRANSITION",
                "message": f"'{current}' 상태에서 '{new_status}'로 변경할 수 없습니다.",
                "current_status": current,
                "allowed_next": allowed_next,
            },
        )

    return order_db.update_status(order_id, new_status)
