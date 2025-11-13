
from user.models import CustomUser
from .models import Todo 

def insert_todo(todo_name:str, user:CustomUser) -> None:
    is_todo = Todo.objects.filter(
        user=user, todo_name=todo_name
    )

    if is_todo:
        raise ValueError(f"{todo_name}은 이미 존재합니다.")

    new_todo = Todo(user=user, todo_name=todo_name)
    new_todo.save()

def select_todos(user:CustomUser) -> list:
    return Todo.objects.filter(
        user=user
    )

def get_todo(user:CustomUser, id:int) -> CustomUser:
    return Todo.objects.get(
        user=user, id=id
    )
