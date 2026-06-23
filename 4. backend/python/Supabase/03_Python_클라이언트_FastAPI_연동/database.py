import os

from dotenv import load_dotenv
from supabase import Client, create_client

# .env 파일의 환경 변수를 현재 프로세스에 불러옵니다.
load_dotenv()

# 필수 환경 변수가 없으면 서버 시작 시 KeyError가 발생합니다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Service Role Key는 관리자 권한을 가지므로 서버에서만 사용해야 합니다.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
