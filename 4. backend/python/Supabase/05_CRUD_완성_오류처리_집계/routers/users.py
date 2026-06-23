from fastapi import APIRouter, Depends
from supabase import Client

from database import get_supabase
from repository import SupabaseRepository
from schemas import ChatSummary, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


def get_repo(db: Client = Depends(get_supabase)) -> SupabaseRepository:
    """FastAPI가 get_supabase를 호출해 만든 db로 Repository를 조립한다."""
    return SupabaseRepository(db)


# @router.post()가 HTTP POST 메서드와 /users 경로를 연결한다.
# status_code=201은 새 자원이 생성되었다는 의미다.
@router.post("", status_code=201)
def create_user(data: UserCreate, repo: SupabaseRepository = Depends(get_repo)):
    return repo.create_user(data)


@router.get("/{user_id}")
def get_user(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.get_user(user_id)


# app.patch()가 HTTP 메서드를 PATCH로 정하고, 부분 수정 동작은 update_user() 안의
# exclude_unset=True가 요청에서 생략한 필드를 UPDATE 대상에서 제외해 구현한다.
@router.patch("/{user_id}")
def update_user(user_id: str, data: UserUpdate, repo: SupabaseRepository = Depends(get_repo)):
    return repo.update_user(user_id, data)


# response_model은 반환값을 ChatSummary 구조로 검증하며 Swagger에도 응답 형식을 표시한다.
@router.get("/{user_id}/summary", response_model=ChatSummary)
def get_summary(user_id: str, repo: SupabaseRepository = Depends(get_repo)):
    return repo.summary(user_id)
