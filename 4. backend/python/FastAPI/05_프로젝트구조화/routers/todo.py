from fastapi import APIRouter, HTTPException
from schemas.todo import TodoCreate, TodoResponse, TodoListResponse
from models.todo import todo_db

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


@router.get("", response_model=TodoListResponse)
def get_todos(skip: int = 0, limit: int = 10):
    """할 일 목록 조회 (페이지네이션)"""
    return TodoListResponse(
        total=todo_db.count(),
        items=todo_db.get_all(skip=skip, limit=limit),
    )


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    """특정 할 일 조회"""
    todo = todo_db.get_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    return todo


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate):
    """할 일 생성"""
    return todo_db.create(
        title=todo.title,
        description=todo.description,
        priority=todo.priority,
    )
