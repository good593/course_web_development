"""
2교시 실습 서버: HTTP Method 이해

curl / HTTPie 실습용 서버입니다.

실행: uvicorn main:app --reload
"""
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="HTTP Method 실습 API",
    description="curl / HTTPie로 HTTP 메서드를 직접 실습하는 서버",
    version="0.1.0",
)

# ── 인메모리 데이터 ──────────────────────────────────────────────────────────

items_db: dict[int, dict] = {
    1: {"id": 1, "name": "노트북",  "price": 1500000, "in_stock": True},
    2: {"id": 2, "name": "마우스",  "price": 35000,   "in_stock": True},
    3: {"id": 3, "name": "키보드", "price": 89000,   "in_stock": False},
}
next_id = 4


# ── Pydantic 스키마 ──────────────────────────────────────────────────────────

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="아이템 이름")
    price: float = Field(gt=0, description="가격 (0 초과)")
    in_stock: bool = Field(default=True, description="재고 여부")


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    price: Optional[float] = Field(default=None, gt=0)
    in_stock: Optional[bool] = None


# ── GET ─────────────────────────────────────────────────────────────────────

@app.get("/", summary="루트 — 서버 확인")
def read_root():
    return {"message": "HTTP Method 실습 서버에 오신 것을 환영합니다!"}


@app.get("/items", summary="아이템 목록 조회 (Query Parameter 실습)")
def get_items(
    keyword: Optional[str] = None,
    in_stock: Optional[bool] = None,
):
    """
    Query Parameter로 필터링:
    - **keyword**: 이름에 포함된 키워드
    - **in_stock**: 재고 여부 (`true` / `false`)
    """
    results = list(items_db.values())

    if keyword:
        results = [i for i in results if keyword in i["name"]]
    if in_stock is not None:
        results = [i for i in results if i["in_stock"] == in_stock]

    return {"total": len(results), "items": results}


@app.get("/search", summary="키워드 검색 (Query String 실습)")
def search(keyword: str = ""):
    """URL에 keyword 쿼리 파라미터를 포함해 검색합니다."""
    results = [i for i in items_db.values() if keyword.lower() in i["name"].lower()]
    return {"keyword": keyword, "results": results}


@app.get("/items/{item_id}", summary="아이템 단건 조회 (Path Parameter 실습)")
def get_item(item_id: int):
    """
    Path Parameter로 특정 아이템을 조회합니다.
    - 존재하지 않으면 **404** 반환
    - 숫자 아닌 값이면 **422** 반환
    """
    item = items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


# ── POST ─────────────────────────────────────────────────────────────────────

@app.post("/items", status_code=201, summary="아이템 생성 (Request Body 실습)")
def create_item(item: ItemCreate):
    """
    Request Body에 JSON을 담아 아이템을 생성합니다.
    - 성공 시 **201 Created** 반환
    - 필수 필드 누락 또는 타입 오류 시 **422** 반환
    """
    global next_id
    new_item = {
        "id": next_id,
        **item.model_dump(),
        "created_at": datetime.now().isoformat(),
    }
    items_db[next_id] = new_item
    next_id += 1
    return new_item


# ── PUT ──────────────────────────────────────────────────────────────────────

@app.put("/items/{item_id}", summary="아이템 전체 수정 (PUT 실습)")
def replace_item(item_id: int, item: ItemCreate):
    """전체 필드를 교체합니다. 존재하지 않으면 404."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    updated = {"id": item_id, **item.model_dump()}
    items_db[item_id] = updated
    return updated


# ── PATCH ────────────────────────────────────────────────────────────────────

@app.patch("/items/{item_id}", summary="아이템 부분 수정 (PATCH 실습)")
def update_item(item_id: int, item: ItemUpdate):
    """보낸 필드만 수정합니다. 나머지 필드는 그대로 유지됩니다."""
    stored = items_db.get(item_id)
    if not stored:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    update_data = item.model_dump(exclude_none=True)
    stored.update(update_data)
    return stored


# ── DELETE ───────────────────────────────────────────────────────────────────

@app.delete("/items/{item_id}", status_code=204, summary="아이템 삭제 (DELETE 실습)")
def delete_item(item_id: int):
    """아이템을 삭제합니다. 성공 시 **204 No Content** 반환."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    del items_db[item_id]


# ── 상태 코드 데모 ────────────────────────────────────────────────────────────

@app.get("/status/{code}", summary="HTTP 상태 코드 체험")
def return_status(code: int):
    """
    원하는 상태 코드로 응답을 받아볼 수 있습니다.
    예: GET /status/404  → 404 Not Found 응답
    """
    messages = {
        200: "OK — 요청 성공",
        201: "Created — 리소스 생성 성공",
        204: "No Content — 성공했지만 본문 없음",
        400: "Bad Request — 잘못된 요청",
        401: "Unauthorized — 인증 필요",
        403: "Forbidden — 권한 없음",
        404: "Not Found — 리소스 없음",
        409: "Conflict — 충돌 (중복 등)",
        422: "Unprocessable Entity — 데이터 검증 실패",
        500: "Internal Server Error — 서버 오류",
    }
    if code not in messages:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 상태 코드입니다: {code}")
    raise HTTPException(status_code=code, detail=messages[code])
