"""
Streamlit 세션에 저장할 채팅 메시지를 만드는 작은 도우미입니다.
"""

from typing import Literal

ChatRole = Literal["user", "assistant"]


def create_message(role: ChatRole, content: str) -> dict[str, str] | None:
    # FastAPI의 ChatMessage 스키마와 같은 모양으로 맞춥니다.
    if role not in {"user", "assistant"}:
        return None
    # 빈 문자열은 대화 기록에 넣지 않습니다.
    if not isinstance(content, str) or not content.strip():
        return None
    return {"role": role, "content": content}
