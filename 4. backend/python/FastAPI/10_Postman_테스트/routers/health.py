from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="서버 상태 확인",
    response_description="서버 상태 정보",
)
def health_check():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.now().isoformat()}
