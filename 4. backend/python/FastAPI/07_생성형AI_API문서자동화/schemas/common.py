from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """FastAPI가 기본으로 반환하는 오류 응답 모양입니다."""

    # 성공 응답뿐 아니라 오류 응답도 예시를 넣어 두면 Swagger 문서가 더 친절해집니다.
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"detail": "상품을 찾을 수 없습니다."},
                {
                    "detail": {
                        "code": "INSUFFICIENT_STOCK",
                        "product_id": 1,
                        "available": 2,
                        "requested": 5,
                    }
                },
            ]
        }
    )

    detail: str | dict[str, Any] | list[dict[str, Any]] = Field(
        description="오류 메시지 또는 검증 오류 상세 정보"
    )


# 여러 라우터에서 반복해서 쓰는 공통 오류 응답 설명입니다.
COMMON_ERRORS = {
    401: {"description": "인증 토큰 없음 또는 만료", "model": ErrorResponse},
    403: {"description": "권한 없음", "model": ErrorResponse},
    422: {"description": "요청 데이터 형식 오류"},
    500: {"description": "서버 내부 오류"},
}
