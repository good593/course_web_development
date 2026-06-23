import os

from dotenv import load_dotenv

load_dotenv()

# 필수 Supabase 값은 누락 시 즉시 실패시키고, 실습용 TTL 값에는 기본값을 둡니다.
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 앱 세션이 Redis에 유지되는 시간(초)입니다. 요청이 올 때마다 갱신됩니다.
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))

# Redis에 보관하는 최근 메시지 수와 캐시 유지 시간입니다.
RECENT_HISTORY_LIMIT = int(os.getenv("RECENT_HISTORY_LIMIT", "20"))
RECENT_HISTORY_TTL_SECONDS = int(os.getenv("RECENT_HISTORY_TTL_SECONDS", "86400"))
