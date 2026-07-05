from datetime import datetime

from fastapi import APIRouter

from core.metadata import API_VERSION

# Health 라우터는 서버가 켜져 있는지 빠르게 확인하는 용도로 사용합니다.
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="서버 상태 확인",
    response_description="서버 상태 정보",
)
def health_check() -> dict[str, str]:
    # 외부 모니터링 도구나 학생의 브라우저 테스트에서 가장 먼저 호출하기 좋은 엔드포인트입니다.
    return {"status": "ok", "version": API_VERSION, "timestamp": datetime.now().isoformat()}
