from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import public_client
from schemas import CurrentUser

# Authorization: Bearer {token} 헤더에서 JWT를 추출하는 FastAPI 보안 스키마입니다.
# Depends()와 함께 사용하면 Swagger UI에도 Authorize 버튼이 표시됩니다.
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Bearer 토큰을 Supabase Auth로 검증하고 현재 사용자를 반환합니다."""

    # HTTPBearer가 "Bearer " 접두사를 제거하므로 실제 JWT 문자열만 남습니다.
    # 헤더가 없으면 이 함수가 실행되기 전에 HTTPBearer가 요청을 거부합니다.
    token = credentials.credentials
    try:
        # 토큰의 서명과 만료 시간을 확인하고 토큰 소유자를 가져옵니다.
        result = public_client().auth.get_user(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from exc

    # SDK 호출은 성공했지만 사용자 정보가 없는 경우도 인증 실패로 처리합니다.
    if not result.user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")

    # 엔드포인트가 Supabase SDK 응답 구조에 직접 의존하지 않도록 변환합니다.
    return CurrentUser(
        id=str(result.user.id),
        email=result.user.email or "",
    )
