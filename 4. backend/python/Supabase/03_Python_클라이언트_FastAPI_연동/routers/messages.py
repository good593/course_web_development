from fastapi import APIRouter, HTTPException

from database import supabase
from schemas import MessageCreate

router = APIRouter(tags=["Messages"])


def first_or_404(rows: list[dict], detail: str) -> dict:
    """조회 결과의 첫 행을 반환하고, 결과가 없으면 404 오류를 발생시킵니다."""
    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


@router.post("/conversations/{conversation_id}/messages", status_code=201)
def create_message(conversation_id: str, data: MessageCreate):
    # | 연산자로 요청 본문과 URL의 conversation_id를 하나의 딕셔너리로 합칩니다.
    payload = data.model_dump() | {"conversation_id": conversation_id}
    result = (
        supabase.table("messages")
        .insert(payload)
        .execute()
    )
    return first_or_404(result.data, "메시지가 저장되지 않았습니다")


@router.get("/conversations/{conversation_id}/messages")
def list_messages(conversation_id: str):
    result = (
        supabase.table("messages")
        .select("*")
        # 특정 대화의 메시지만 조회하며, desc를 생략한 order()의 기본값은 오름차순입니다.
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    )
    return result.data
