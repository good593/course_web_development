from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

DEMO_ADMIN_TOKEN = "demo-admin-token"

bearer_scheme = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


def require_admin_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    if credentials.credentials != DEMO_ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return credentials.credentials
