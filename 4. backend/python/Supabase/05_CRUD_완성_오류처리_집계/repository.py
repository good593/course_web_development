from fastapi import HTTPException
from supabase import Client

from schemas import (
    ChatSummary,
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
    UserCreate,
    UserUpdate,
)


# table(), select(), eq(), order() 등은 쿼리를 조립하고 execute()가 실제 요청을 보낸다.
# 실행 결과의 data에는 조회되거나 생성·수정된 행이 list[dict] 형태로 담긴다.

class SupabaseRepository:
    """엔드포인트에서 DB 조회 코드와 공통 오류 처리를 분리한다."""

    def __init__(self, db: Client):
        self.db = db

    def one_or_404(self, rows: list[dict], detail: str) -> dict:
        """결과가 없는 경우를 모든 단건 작업에서 같은 방식으로 처리한다."""
        if not rows:
            raise HTTPException(status_code=404, detail=detail)
        return rows[0]

    # ── 사용자 ──────────────────────────────────────────────────────────

    def create_user(self, data: UserCreate) -> dict:
        result = (
            self.db.table("app_users")
            .insert(data.model_dump())
            .execute()
        )
        return self.one_or_404(result.data, "사용자가 생성되지 않았습니다")

    def get_user(self, user_id: str) -> dict:
        result = (
            self.db.table("app_users")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        return self.one_or_404(result.data, "사용자를 찾을 수 없습니다")

    def update_user(self, user_id: str, data: UserUpdate) -> dict:
        # model_dump()만 쓰면 생략한 display_name도 기본값 None으로 포함된다.
        # exclude_unset=True는 JSON에 없던 필드를 빼서 그 필드의 기존 값 덮어쓰기를 막는다.
        payload = data.model_dump(exclude_unset=True)
        # 빈 JSON 객체 {}처럼 수정할 필드가 하나도 없으면 불필요한 UPDATE를 실행하지 않는다.
        if not payload:
            raise HTTPException(status_code=400, detail="수정할 값이 없습니다")
        result = (
            self.db.table("app_users")
            .update(payload)
            .eq("id", user_id)
            # supabase-py 2.x는 수정된 행을 result.data에 반환하므로 select를 덧붙이지 않는다.
            .execute()
        )
        return self.one_or_404(result.data, "사용자를 찾을 수 없습니다")

    # ── 대화방 ──────────────────────────────────────────────────────────

    def create_conversation(self, user_id: str, data: ConversationCreate) -> dict:
        # 먼저 부모 사용자를 조회해야 존재하지 않는 user_id에 명확한 404를 반환할 수 있다.
        self.get_user(user_id)
        # 요청 본문에는 없는 URL의 user_id를 | 연산자로 합쳐 외래 키로 저장한다.
        payload = data.model_dump() | {"user_id": user_id}
        result = (
            self.db.table("conversations")
            .insert(payload)
            .execute()
        )
        return self.one_or_404(result.data, "대화방이 생성되지 않았습니다")

    def list_conversations(self, user_id: str) -> list[dict]:
        # 대화방이 0개인 사용자와 존재하지 않는 사용자를 구분하기 위해 먼저 조회한다.
        self.get_user(user_id)
        result = (
            self.db.table("conversations")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    def get_conversation(self, conversation_id: str) -> dict:
        result = (
            self.db.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .limit(1)
            .execute()
        )
        return self.one_or_404(result.data, "대화방을 찾을 수 없습니다")

    def update_conversation(self, conversation_id: str, data: ConversationUpdate) -> dict:
        # 수정 필드가 title 하나이고 스키마에서 필수이므로 여기서는 exclude_unset이 필요 없다.
        result = (
            self.db.table("conversations")
            .update(data.model_dump())
            .eq("id", conversation_id)
            .execute()
        )
        return self.one_or_404(result.data, "대화방을 찾을 수 없습니다")

    # ── 메시지 ──────────────────────────────────────────────────────────

    def create_message(self, conversation_id: str, data: MessageCreate) -> dict:
        # 먼저 부모 대화방을 조회해야 잘못된 conversation_id에 명확한 404를 반환할 수 있다.
        self.get_conversation(conversation_id)
        # URL의 conversation_id를 요청 데이터와 합쳐 메시지의 외래 키로 저장한다.
        payload = data.model_dump() | {"conversation_id": conversation_id}
        result = (
            self.db.table("messages")
            .insert(payload)
            .execute()
        )
        return self.one_or_404(result.data, "메시지가 저장되지 않았습니다")

    def list_messages(self, conversation_id: str, limit: int) -> list[dict]:
        # 메시지가 0개인 대화방과 존재하지 않는 대화방을 구분하기 위해 먼저 조회한다.
        self.get_conversation(conversation_id)
        result = (
            self.db.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            # order()의 기본값은 오름차순이므로 오래된 메시지부터 limit개를 가져온다.
            .order("created_at")
            .limit(limit)
            .execute()
        )
        return result.data

    # ── 집계 ────────────────────────────────────────────────────────────

    def summary(self, user_id: str) -> ChatSummary:
        # list_conversations()를 재사용해 사용자 존재 확인과 대화방 조회를 함께 처리한다.
        conversations = self.list_conversations(user_id)
        message_count = 0
        for conversation in conversations:
            # 메시지 내용은 필요 없으므로 id만 받고, 반환된 행의 길이로 개수를 센다.
            # 학습을 위한 단순한 방식이며 대화방 수만큼 메시지 조회 쿼리가 실행된다.
            result = (
                self.db.table("messages")
                .select("id")
                .eq("conversation_id", conversation["id"])
                .execute()
            )
            message_count += len(result.data)
        return ChatSummary(
            user_id=user_id,
            conversation_count=len(conversations),
            message_count=message_count,
        )
