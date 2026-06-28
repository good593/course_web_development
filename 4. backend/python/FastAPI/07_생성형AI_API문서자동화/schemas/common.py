from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict


COMMON_ERRORS = {
    401: {"description": "인증 토큰 없음 또는 만료", "model": ErrorResponse},
    403: {"description": "권한 없음", "model": ErrorResponse},
    422: {"description": "요청 데이터 형식 오류"},
    500: {"description": "서버 내부 오류"},
}
