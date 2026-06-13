from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Item API - GET 실습", version="0.1.0")

fake_db: dict[int, dict] = {
    1: {"id": 1, "name": "노트북", "price": 1500000, "category": "전자기기", "in_stock": True},
    2: {"id": 2, "name": "마우스", "price": 35000,   "category": "전자기기", "in_stock": True},
    3: {"id": 3, "name": "책상",   "price": 250000,  "category": "가구",     "in_stock": False},
    4: {"id": 4, "name": "의자",   "price": 180000,  "category": "가구",     "in_stock": True},
}


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str
    in_stock: bool


# /search를 /{item_id}보다 먼저 선언해야 충돌 없음
@app.get("/items/search", response_model=List[ItemResponse])
def search_items(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    in_stock: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    """아이템 검색 (다중 Query Parameter 필터)"""
    results = list(fake_db.values())

    if keyword:
        results = [i for i in results if keyword in i["name"]]
    if category:
        results = [i for i in results if i["category"] == category]
    if in_stock is not None:
        results = [i for i in results if i["in_stock"] == in_stock]
    if min_price is not None:
        results = [i for i in results if i["price"] >= min_price]
    if max_price is not None:
        results = [i for i in results if i["price"] <= max_price]

    return results


@app.get("/items", response_model=List[ItemResponse])
def get_items(skip: int = 0, limit: int = 10):
    """아이템 목록 조회 (페이지네이션)"""
    items = list(fake_db.values())
    return items[skip : skip + limit]


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    """특정 아이템 단건 조회"""
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return fake_db[item_id]
