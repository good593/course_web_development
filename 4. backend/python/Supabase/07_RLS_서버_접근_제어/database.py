import os

from dotenv import load_dotenv
from supabase import Client, create_client

# .env 파일의 Supabase 접속 정보를 현재 프로세스의 환경변수로 불러옵니다.
load_dotenv()

# anon key는 Auth 요청에, service_role key는 신뢰할 수 있는 서버의 DB 작업에 사용합니다.
# service_role key는 RLS를 우회하므로 브라우저나 앱 클라이언트에 절대 노출하면 안 됩니다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def public_client() -> Client:
    """anon key로 회원가입, 로그인, JWT 사용자 조회를 수행합니다."""

    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def admin_client() -> Client:
    """service_role key로 서버 측 DB 작업을 수행합니다."""

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
