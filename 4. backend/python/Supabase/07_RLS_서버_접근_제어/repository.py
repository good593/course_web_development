from fastapi import HTTPException

from database import admin_client


def one_or_404(rows: list[dict], detail: str) -> dict:
    """Supabase 결과의 첫 행을 반환하고, 결과가 없으면 404로 변환합니다."""

    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


def upsert_profile(user_id: str, email: str, display_name: str) -> dict:
    """Auth 사용자와 1:1로 연결되는 public.profiles 행을 저장합니다."""

    # upsert는 같은 id가 있으면 수정하고, 없으면 새 행을 추가합니다.
    result = (
        admin_client()
        .table("profiles")
        .upsert({
            "id": user_id,
            "email": email,
            "display_name": display_name,
        })
        .execute()
    )
    return one_or_404(result.data, "프로필을 저장하지 못했습니다")


def get_owned_conversation(conversation_id: str, user_id: str) -> dict:
    """현재 사용자가 소유한 대화방을 조회하고, 아니면 404를 반환합니다."""

    # admin_client는 RLS를 우회하므로 id만 조회하면 다른 사용자의 방도 반환됩니다.
    # 반드시 owner_id 조건을 함께 적용하여 서버에서 소유권을 검사해야 합니다.
    result = (
        admin_client()
        .table("chat_conversations")
        .select("*")
        .eq("id", conversation_id)
        .eq("owner_id", user_id)
        .limit(1)
        .execute()
    )
    return one_or_404(result.data, "대화방을 찾을 수 없습니다")
