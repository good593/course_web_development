from datetime import datetime


class ProductDB:
    def __init__(self):
        self._categories: dict[int, dict] = {
            1: {"id": 1, "name": "전자제품", "slug": "electronics"},
            2: {"id": 2, "name": "의류", "slug": "clothing"},
            3: {"id": 3, "name": "식품", "slug": "food"},
        }
        self._products: dict[int, dict] = {}
        self._next_id = 1

    def list_categories(self) -> list[dict]:
        return list(self._categories.values())

    def has_category(self, category_id: int) -> bool:
        return category_id in self._categories

    def sku_exists(self, sku: str) -> bool:
        return any(product["sku"] == sku for product in self._products.values())

    def create(self, product_data: dict) -> dict:
        product = {
            "id": self._next_id,
            **product_data,
            "created_at": datetime.now(),
        }
        self._products[self._next_id] = product
        self._next_id += 1
        return product

    def get_all(self, status: str | None = None, category_id: int | None = None) -> list[dict]:
        products = list(self._products.values())

        if status:
            products = [product for product in products if product["status"] == status]
        if category_id:
            products = [
                product for product in products if product.get("category_id") == category_id
            ]

        return products

    def get_by_id(self, product_id: int) -> dict | None:
        return self._products.get(product_id)

    def update(self, product_id: int, update_data: dict) -> dict | None:
        product = self.get_by_id(product_id)
        if not product:
            return None

        product.update(update_data)
        return product

    def delete(self, product_id: int) -> bool:
        if product_id not in self._products:
            return False

        del self._products[product_id]
        return True

    def build_response(self, product: dict) -> dict:
        category_data = self._categories.get(product.get("category_id"))
        return {
            **product,
            "category": category_data,
            "discount_rate": self.compute_discount_rate(
                product["original_price"],
                product.get("sale_price"),
            ),
        }

    @staticmethod
    def compute_discount_rate(original: int, sale: int | None) -> float | None:
        if sale is None:
            return None
        return round((1 - sale / original) * 100, 1)


# 애플리케이션 전체에서 공유하는 인스턴스
product_db = ProductDB()
