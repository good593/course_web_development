from fastapi import APIRouter, HTTPException

from models.user import user_db
from schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    if user_db.email_exists(user.email):
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")

    if user_db.username_exists(user.username):
        raise HTTPException(status_code=409, detail="이미 사용 중인 사용자명입니다.")

    return user_db.create(user.model_dump())


@router.get("", response_model=list[UserResponse])
def list_users():
    return user_db.get_all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    user = user_db.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, update: UserUpdate):
    user = user_db.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if not user["active"]:
        raise HTTPException(status_code=403, detail="비활성화된 계정은 수정할 수 없습니다.")

    if update.username and user_db.username_exists(update.username, exclude_user_id=user_id):
        raise HTTPException(status_code=409, detail="이미 사용 중인 사용자명입니다.")

    update_data = update.model_dump(exclude_none=True)
    return user_db.update(user_id, update_data)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    if not user_db.delete(user_id):
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: int):
    user = user_db.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if not user["active"]:
        raise HTTPException(status_code=400, detail="이미 비활성화된 계정입니다.")

    return user_db.deactivate(user_id)
