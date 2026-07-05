from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# 실습용 고정 토큰입니다. 실제 서비스라면 JWT 검증이나 DB 조회로 바꿉니다.
DEMO_ADMIN_TOKEN = "demo-admin-token"

# auto_error=False로 두면 토큰이 없을 때 FastAPI 기본 오류 대신 직접 설명을 줄 수 있습니다.
bearer_scheme = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


def require_admin_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    """관리자 권한이 필요한 엔드포인트에서 공통으로 사용하는 인증 함수입니다."""
    if not credentials:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    if credentials.credentials != DEMO_ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return credentials.credentials
