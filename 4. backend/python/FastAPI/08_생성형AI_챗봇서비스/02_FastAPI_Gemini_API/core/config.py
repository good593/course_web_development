import os

from dotenv import load_dotenv

load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f".env 파일에 {name}=... 값을 넣어주세요.")
    return value


GEMINI_API_KEY = get_required_env("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))
DEFAULT_SYSTEM_INSTRUCTION = os.getenv(
    "GEMINI_SYSTEM_INSTRUCTION",
    "친절하고 유능한 AI 어시스턴트입니다.",
)
