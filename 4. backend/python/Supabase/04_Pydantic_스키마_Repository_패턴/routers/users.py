# Depends: 의존성 주입에 사용합니다.
from fastapi import APIRouter, Depends

from database import get_supabase
from repository import SupabaseRepository
from schemas import UserCreate
from supabase import Client

router = APIRouter(prefix="/users", tags=["Users"])


def get_repo(db: Client = Depends(get_supabase)) -> SupabaseRepository:
    # FastAPI가 get_supabase()의 결과를 db에 넣고 Repository를 만들어 줍니다.
    return SupabaseRepository(db)


# 새 사용자를 생성하며 성공 시 HTTP 201 Created를 반환합니다.
@router.post("", status_code=201)
def create_user(data: UserCreate, repo: SupabaseRepository = Depends(get_repo)):
    # Depends가 get_repo()를 호출해 현재 요청에서 사용할 Repository를 주입합니다.
    return repo.create_user(data)


# 등록된 사용자 목록을 최신순으로 조회합니다.
@router.get("")
def list_users(repo: SupabaseRepository = Depends(get_repo)):
    return repo.list_users()


# 중괄호로 감싼 user_id는 URL에서 함수 인자로 전달되는 경로 매개변수입니다.
@router.get("/{user_id}")
def get_user(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.get_user(user_id)
