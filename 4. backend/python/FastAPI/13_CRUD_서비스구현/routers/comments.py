from fastapi import APIRouter, Depends

import schemas
from core.dependencies import get_post_service
from services import PostService

router = APIRouter(
    prefix="/posts/{post_id}/comments",
    tags=["Comments"],
)


@router.get(
    "",
    response_model=list[schemas.CommentResponse],
    summary="게시글 댓글 목록",
)
def list_comments(post_id: int, service: PostService = Depends(get_post_service)):
    return service.list_comments(post_id)


@router.post(
    "",
    response_model=schemas.CommentResponse,
    status_code=201,
    summary="댓글 작성 (공개 게시글만)",
)
def add_comment(post_id: int, data: schemas.CommentCreate, service: PostService = Depends(get_post_service)):
    return service.add_comment(post_id, data)


@router.delete(
    "/{comment_id}",
    status_code=204,
    summary="댓글 삭제",
)
def delete_comment(post_id: int, comment_id: int, service: PostService = Depends(get_post_service)):
    service.delete_comment(post_id, comment_id)
