from supabase import Client, create_client

from config import SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL


def public_client() -> Client:
    # 회원가입, 로그인, 토큰 검증은 공개용 anon 키로 Supabase Auth를 호출합니다.
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def admin_client() -> Client:
    # service_role은 RLS를 우회하므로 서버 내부에서만 사용해야 합니다.
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
