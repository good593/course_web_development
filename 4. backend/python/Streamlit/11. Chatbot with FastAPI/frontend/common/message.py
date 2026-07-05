from typing import Literal

ChatRole = Literal["user", "assistant"]


def create_message(role: ChatRole, content: str) -> dict[str, str] | None:
    if role not in {"user", "assistant"}:
        return None
    if not isinstance(content, str) or not content.strip():
        return None
    return {"role": role, "content": content}
