import time
from uuid import uuid4

from fastapi import HTTPException
from google.genai import types

from core.config import DEFAULT_SYSTEM_INSTRUCTION, GEMINI_MODEL, SESSION_TTL_SECONDS
from core.gemini import client
from models import SessionData
from schemas import SessionCreateResponse, SessionSummary

sessions: dict[str, SessionData] = {}


def get_session(session_id: str) -> SessionData:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"세션을 찾을 수 없습니다: {session_id}")

    session = sessions[session_id]
    session.last_used = time.time()
    return session


def cleanup_sessions() -> int:
    now = time.time()
    expired = [
        session_id
        for session_id, session in sessions.items()
        if now - session.last_used > SESSION_TTL_SECONDS
    ]

    for session_id in expired:
        del sessions[session_id]

    return len(expired)


def create_session(
    system_instruction: str = DEFAULT_SYSTEM_INSTRUCTION,
) -> SessionCreateResponse:
    cleanup_sessions()

    session_id = str(uuid4())
    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )
    sessions[session_id] = SessionData(
        chat=chat,
        system_instruction=system_instruction,
    )

    return SessionCreateResponse(
        session_id=session_id,
        message="세션이 생성되었습니다.",
    )


def delete_session(session_id: str) -> dict[str, str]:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    del sessions[session_id]
    return {"message": f"세션 {session_id}가 삭제되었습니다."}


def list_active_sessions() -> list[SessionSummary]:
    now = time.time()

    return [
        SessionSummary(
            session_id=session_id,
            created_ago_sec=int(now - session.created_at),
            last_used_ago_sec=int(now - session.last_used),
            history_turns=len(session.chat.get_history()),
        )
        for session_id, session in sessions.items()
    ]


def active_session_count() -> int:
    return len(sessions)
