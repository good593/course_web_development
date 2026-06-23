from fastapi import APIRouter, Depends, Query
from supabase import Client

from database import get_supabase
from repository import SupabaseRepository
from schemas import MessageCreate

router = APIRouter(tags=["Messages"])


def get_repo(db: Client = Depends(get_supabase)) -> SupabaseRepository:
    """FastAPI가 get_supabase를 호출해 만든 db로 Repository를 조립한다."""
    return SupabaseRepository(db)


@router.post("/conversations/{conversation_id}/messages", status_code=201)
def create_message(
    conversation_id: str,
    data: MessageCreate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.create_message(conversation_id, data)


@router.get("/conversations/{conversation_id}/messages")
def list_messages(
    conversation_id: str,
    # Query()를 사용했으므로 limit는 ?limit=20 형태의 쿼리 파라미터가 된다.
    # 생략하면 50을 쓰고, ge=1과 le=100 범위를 벗어나면 FastAPI가 422를 반환한다.
    limit: int = Query(50, ge=1, le=100),
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.list_messages(conversation_id, limit)
