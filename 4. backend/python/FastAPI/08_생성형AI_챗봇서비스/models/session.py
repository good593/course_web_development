import time
from dataclasses import dataclass, field


@dataclass
class SessionData:
    chat: object
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    system_instruction: str = "친절하고 유능한 AI 어시스턴트입니다."
