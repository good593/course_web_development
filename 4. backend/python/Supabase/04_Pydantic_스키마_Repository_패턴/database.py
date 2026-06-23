# 운영체제의 환경 변수에 접근하기 위한 표준 라이브러리입니다.
import os

# 프로젝트 루트의 .env 파일을 읽어 환경 변수로 등록합니다.
from dotenv import load_dotenv
# Client는 타입 표시에, create_client는 Supabase 클라이언트 생성에 사용합니다.
from supabase import Client, create_client

# .env 파일의 값을 환경 변수로 불러옵니다.
load_dotenv()

# 환경 변수가 없으면 서버 시작 시 바로 오류가 발생하므로 설정 누락을 빠르게 알 수 있습니다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def get_supabase() -> Client:
    # 요청 처리에 사용할 Supabase 클라이언트를 생성하는 의존성 함수입니다.
    # URL은 프로젝트 위치, Service Role Key는 서버의 DB 접근 권한을 전달합니다.
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
