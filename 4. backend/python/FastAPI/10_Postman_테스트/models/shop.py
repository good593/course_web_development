from datetime import datetime

from schemas.order import OrderCreate
from schemas.product import ProductCreate, ProductUpdate
from schemas.user import UserCreate


class ShopDB:
    def __init__(self):
        self.products: dict[int, dict] = {
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
        self.orders: dict[int, dict] = {}
        self.users: dict[int, dict] = {}
        self._next_ids = {"product": 3, "order": 1, "user": 1}

    def list_products(self, category: str | None, page: int, size: int) -> list[dict]:
        items = list(self.products.values())
        if category:
            items = [product for product in items if product["category"] == category]

        start = (page - 1) * size
        return items[start : start + size]

    def create_product(self, product: ProductCreate) -> dict:
        product_id = self._next_ids["product"]
        self._next_ids["product"] += 1

        new_product = {
            "id": product_id,
            **product.model_dump(),
            "created_at": datetime.now(),
        }
        self.products[product_id] = new_product
        return new_product

    def get_product(self, product_id: int) -> dict | None:
        return self.products.get(product_id)

    def update_product(self, product_id: int, update: ProductUpdate) -> dict | None:
        product = self.get_product(product_id)
        if not product:
            return None

        product.update(update.model_dump(exclude_none=True))
        return product

    def delete_product(self, product_id: int) -> bool:
        if product_id not in self.products:
            return False

        del self.products[product_id]
        return True

    def product_name_exists(self, name: str) -> bool:
        return any(product["name"] == name for product in self.products.values())

    def create_order(self, order: OrderCreate) -> dict:
        items_detail = []
        total = 0

        for item in order.items:
            product = self.products[item.product_id]
            total += product["price"] * item.quantity
            items_detail.append(
                {
                    "product_id": item.product_id,
                    "name": product["name"],
                    "quantity": item.quantity,
                    "unit_price": product["price"],
                }
            )

        for item in order.items:
            self.products[item.product_id]["stock"] -= item.quantity

        order_id = self._next_ids["order"]
        self._next_ids["order"] += 1
        new_order = {
            "id": order_id,
            "items": items_detail,
            "total_price": total,
            "status": "pending",
            "created_at": datetime.now(),
        }
        self.orders[order_id] = new_order
        return new_order

    def get_order(self, order_id: int) -> dict | None:
        return self.orders.get(order_id)

    def email_exists(self, email: str) -> bool:
        return any(user["email"] == email for user in self.users.values())

    def create_user(self, user: UserCreate) -> dict:
        user_id = self._next_ids["user"]
        self._next_ids["user"] += 1

        new_user = {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "created_at": datetime.now(),
        }
        self.users[user_id] = new_user
        return new_user


# 애플리케이션 전체에서 공유하는 인메모리 저장소
shop_db = ShopDB()
