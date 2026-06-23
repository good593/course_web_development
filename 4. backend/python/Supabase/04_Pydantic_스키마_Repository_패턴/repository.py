from fastapi import HTTPException
from supabase import Client

from schemas import ConversationCreate, MessageCreate, UserCreate


# 데이터베이스 접근과 쿼리 로직을 엔드포인트에서 분리해 한곳에 모읍니다.
class SupabaseRepository:
    def __init__(self, db: Client):
        # 외부에서 클라이언트를 주입받아 실제 객체나 테스트용 객체로 교체할 수 있습니다.
        self.db = db

    def one_or_404(self, rows: list[dict], detail: str) -> dict:
        # 단건 조회 결과가 비어 있으면 일관된 형식의 404 응답을 만듭니다.
        if not rows:
            raise HTTPException(status_code=404, detail=detail)
        return rows[0]

    # ── 사용자 ──────────────────────────────────────────────────────────

    def create_user(self, data: UserCreate) -> dict:
        # model_dump()는 검증이 끝난 Pydantic 모델을 DB에 넣을 dict로 변환합니다.
        result = (
            # app_users 테이블에 사용자 데이터를 추가할 쿼리를 만듭니다.
            self.db.table("app_users")
            .insert(data.model_dump())
            # insert는 기본적으로 저장된 행을 반환하며, execute가 요청을 전송합니다.
            .execute()
        )
        # result.data는 행의 목록이므로 첫 번째 행을 꺼내 반환합니다.
        return self.one_or_404(result.data, "사용자가 생성되지 않았습니다")

    def get_user(self, user_id: str) -> dict:
        # 기본 키 id로 사용자 한 명을 조회합니다.
        result = (
            self.db.table("app_users")
            .select("*")
            # eq는 id가 user_id와 같은 행만 필터링합니다.
            .eq("id", user_id)
            # 단건 조회이므로 필요한 행을 최대 1개로 제한합니다.
            .limit(1)
            .execute()
        )
        return self.one_or_404(result.data, "사용자를 찾을 수 없습니다")

    def list_users(self) -> list[dict]:
        # 조건 없이 app_users의 모든 행을 조회합니다.
        result = (
            self.db.table("app_users")
            .select("*")
            # 최신 사용자가 먼저 보이도록 생성 시각을 내림차순 정렬합니다.
            .order("created_at", desc=True)
            .execute()
        )
        # 목록 API이므로 첫 행이 아니라 전체 행 배열을 그대로 반환합니다.
        return result.data

    # ── 대화방 ──────────────────────────────────────────────────────────

    def create_conversation(self, user_id: str, data: ConversationCreate) -> dict:
        # FK 오류를 그대로 노출하지 않고 친절한 404를 주기 위해 사용자를 먼저 조회합니다.
        self.get_user(user_id)
        # 요청 데이터에 URL 경로에서 받은 외래 키를 합쳐 저장할 데이터를 만듭니다.
        payload = data.model_dump() | {"user_id": user_id}
        result = (
            self.db.table("conversations")
            .insert(payload)
            .execute()
        )
        return self.one_or_404(result.data, "대화방이 생성되지 않았습니다")

    def list_conversations(self, user_id: str) -> list[dict]:
        # 존재하지 않는 사용자의 목록 요청도 빈 배열 대신 명확한 404로 응답합니다.
        self.get_user(user_id)
        result = (
            self.db.table("conversations")
            .select("*")
            # 해당 사용자가 만든 대화방만 조회합니다.
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    def get_conversation(self, conversation_id: str) -> dict:
        # 대화방의 기본 키 id로 한 건만 조회합니다.
        result = (
            self.db.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .limit(1)
            .execute()
        )
        return self.one_or_404(result.data, "대화방을 찾을 수 없습니다")

    # ── 메시지 ──────────────────────────────────────────────────────────

    def create_message(self, conversation_id: str, data: MessageCreate) -> dict:
        # 메시지를 저장하기 전에 부모 대화방이 실제로 존재하는지 확인합니다.
        self.get_conversation(conversation_id)
        # 검증된 메시지 데이터에 대화방 외래 키를 추가합니다.
        payload = data.model_dump() | {"conversation_id": conversation_id}
        result = (
            self.db.table("messages")
            .insert(payload)
            .execute()
        )
        return self.one_or_404(result.data, "메시지가 저장되지 않았습니다")

    def list_messages(self, conversation_id: str) -> list[dict]:
        # 존재하지 않는 대화방의 메시지 목록 요청은 404로 처리합니다.
        self.get_conversation(conversation_id)
        result = (
            self.db.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            # 대화 흐름을 읽을 수 있도록 오래된 메시지부터 정렬합니다.
            .order("created_at")
            .execute()
        )
        return result.data
