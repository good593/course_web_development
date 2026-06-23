from fastapi import APIRouter, Depends
from supabase import Client

from database import get_supabase
from repository import SupabaseRepository
from schemas import ConversationCreate, ConversationUpdate

router = APIRouter(tags=["Conversations"])


def get_repo(db: Client = Depends(get_supabase)) -> SupabaseRepository:
    """FastAPI가 get_supabase를 호출해 만든 db로 Repository를 조립한다."""
    return SupabaseRepository(db)


@router.post("/users/{user_id}/conversations", status_code=201)
def create_conversation(
    user_id: str,
    data: ConversationCreate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.create_conversation(user_id, data)


@router.get("/users/{user_id}/conversations")
def list_conversations(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.list_conversations(user_id)


@router.patch("/conversations/{conversation_id}")
def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    repo: SupabaseRepository = Depends(get_repo),
):
    return repo.update_conversation(conversation_id, data)
