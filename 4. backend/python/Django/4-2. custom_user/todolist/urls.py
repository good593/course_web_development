from django.urls import path 

from .views import (
    SelectTodoList, DeleteTodo, UpdateTodo
)

# http://localhost:8000/*
urlpatterns = [
    # http://localhost:8000/
    path("", SelectTodoList.as_view(), name="todolist"),
    # http://localhost:8000/delete/id
    path("delete/<int:id>", DeleteTodo.as_view(), name="delete-task"),
    # http://localhost:8000/update/id
    path("update/<int:id>", UpdateTodo.as_view(), name="update-task"),
]