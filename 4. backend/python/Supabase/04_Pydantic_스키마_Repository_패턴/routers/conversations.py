from fastapi import APIRouter, Depends

from database import get_supabase
from repository import SupabaseRepository
from schemas import ConversationCreate
from supabase import Client

router = APIRouter(tags=["Conversations"])


def get_repo(db: Client = Depends(get_supabase)) -> SupabaseRepository:
    # FastAPI가 get_supabase()의 결과를 db에 넣고 Repository를 만들어 줍니다.
    return SupabaseRepository(db)


# 특정 사용자의 대화방을 생성합니다. data는 요청 본문에서 자동 변환됩니다.
@router.post("/users/{user_id}/conversations", status_code=201)
def create_conversation(
    user_id: str,
    data: ConversationCreate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.create_conversation(user_id, data)


# 특정 사용자가 가진 대화방 목록을 최신순으로 조회합니다.
@router.get("/users/{user_id}/conversations")
def list_conversations(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.list_conversations(user_id)
