from fastapi import APIRouter, HTTPException

from database import supabase
from schemas import ConversationCreate

router = APIRouter(tags=["Conversations"])


def first_or_404(rows: list[dict], detail: str) -> dict:
    """조회 결과의 첫 행을 반환하고, 결과가 없으면 404 오류를 발생시킵니다."""
    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


@router.post("/conversations", status_code=201)
def create_conversation(data: ConversationCreate):
    # 요청 데이터를 conversations 테이블에 새 행으로 저장합니다.
    result = (
        supabase.table("conversations")
        .insert(data.model_dump())
        .execute()
    )
    return first_or_404(result.data, "대화방이 생성되지 않았습니다")


@router.get("/users/{user_id}/conversations")
def list_conversations(user_id: str):
    # {user_id} 값은 같은 이름의 함수 매개변수로 전달됩니다.
    result = (
        supabase.table("conversations")
        .select("*")
        # eq()는 SQL의 WHERE user_id = ... 조건에 해당합니다.
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data
