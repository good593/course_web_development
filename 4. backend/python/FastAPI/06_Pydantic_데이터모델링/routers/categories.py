from fastapi import APIRouter

from models.product import product_db
from schemas.product import Category

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("", response_model=list[Category])
def list_categories():
    return product_db.list_categories()
