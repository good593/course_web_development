from datetime import datetime

from fastapi import APIRouter

from core.metadata import API_VERSION

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="서버 상태 확인",
    response_description="서버 상태 정보",
)
def health_check() -> dict[str, str]:
    return {"status": "ok", "version": API_VERSION, "timestamp": datetime.now().isoformat()}
