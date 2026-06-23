import os

from dotenv import load_dotenv
from supabase import Client, create_client

# .env의 설정값을 os.environ에 넣어 URL과 비밀 키를 코드에 직접 작성하지 않게 한다.
load_dotenv()

# os.environ[이름]은 값이 없을 때 즉시 KeyError를 내므로 잘못된 설정으로 실행되지 않는다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
# service role 키는 서버 전용 비밀 키이므로 브라우저나 공개 저장소에 노출하면 안 된다.
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def get_supabase() -> Client:
    """Depends가 호출할 Supabase 클라이언트 생성 함수다."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
