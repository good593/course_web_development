from django.urls import path 
from .views import todo_list, delete_task, update_task

# http://127.0.0.1:8000/todolist/*
urlpatterns = [
    # http://127.0.0.1:8000/todolist/ 
    path("", todo_list, name="todolist"),
    # http://127.0.0.1:8000/todolist/delete/1
    path("delete/<int:todo_id>", delete_task, name="delete-task"),
    # http://127.0.0.1:8000/todolist/update/1
    path("update/<int:todo_id>", update_task, name="update-task")
]
