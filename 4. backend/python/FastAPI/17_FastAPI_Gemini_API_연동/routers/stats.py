from fastapi import APIRouter

from schemas import StatsResponse
from services.gemini_service import get_usage_stats

router = APIRouter(tags=["Stats"])


@router.get("/stats", response_model=StatsResponse, summary="토큰 사용량 통계")
async def get_stats():
    """누적 토큰 사용량과 예상 비용을 반환합니다."""
    return get_usage_stats()
