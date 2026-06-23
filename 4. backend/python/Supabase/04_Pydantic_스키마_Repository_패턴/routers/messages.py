from fastapi import APIRouter, Depends

from database import get_supabase
from repository import SupabaseRepository
from schemas import MessageCreate
from supabase import Client

router = APIRouter(tags=["Messages"])


def get_repo(db: Client = Depends(get_supabase)) -> SupabaseRepository:
    # FastAPI가 get_supabase()의 결과를 db에 넣고 Repository를 만들어 줍니다.
    return SupabaseRepository(db)


# 특정 대화방에 검증된 역할과 내용으로 새 메시지를 저장합니다.
@router.post("/conversations/{conversation_id}/messages", status_code=201)
def create_message(
    conversation_id: str,
    data: MessageCreate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.create_message(conversation_id, data)


# 특정 대화방의 메시지를 생성 시각 순서대로 조회합니다.
@router.get("/conversations/{conversation_id}/messages")
def list_messages(
    conversation_id: str,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.list_messages(conversation_id)
