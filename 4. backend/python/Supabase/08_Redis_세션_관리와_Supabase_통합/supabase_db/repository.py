from fastapi import HTTPException

from supabase_db.client import admin_client


def one_or_404(rows: list[dict], detail: str) -> dict:
    if not rows:
        raise HTTPException(status_code=404, detail=detail)
    return rows[0]


def upsert_profile(user_id: str, email: str, display_name: str) -> dict:
    # Auth의 user_id를 profiles의 PK로 사용해 인증 사용자와 프로필을 1:1로 연결합니다.
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
    return one_or_404(result.data, "프로필 저장에 실패했습니다")


def get_owned_conversation(conversation_id: str, user_id: str) -> dict:
    # admin_client는 RLS를 우회하므로 모든 조회에 owner_id 조건을 직접 적용합니다.
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
