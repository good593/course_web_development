ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["processing", "cancelled"],
    "processing": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": [],
    "cancelled": [],
}


class OrderDB:
    def __init__(self):
        self._data: dict[int, dict] = {
            1: {"id": 1, "status": "pending", "user_id": 1, "total": 50000},
            2: {"id": 2, "status": "shipped", "user_id": 1, "total": 120000},
        }

    def allowed_statuses(self) -> list[str]:
        return list(ALLOWED_TRANSITIONS.keys())

    def allowed_next_statuses(self, current_status: str) -> list[str]:
        return ALLOWED_TRANSITIONS[current_status]

    def get_by_id(self, order_id: int) -> dict | None:
        return self._data.get(order_id)

    def update_status(self, order_id: int, status: str) -> dict | None:
        order = self.get_by_id(order_id)
        if not order:
            return None

        order["status"] = status
        return order


# 애플리케이션 전체에서 공유하는 인스턴스
order_db = OrderDB()
