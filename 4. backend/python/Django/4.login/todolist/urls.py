from django.urls import path 

from .views import (
    search_todolist,
    delete_todo,
    update_todo
)

# http://127.0.0.1:8000/*
urlpatterns = [
    # http://127.0.0.1:8000/
    path("", search_todolist, name="todolist"),
    # http://127.0.0.1:8000/delete/id
    path("delete/<int:id>", delete_todo, name="delete-task"),
    # http://127.0.0.1:8000/update/id
    path("update/<int:id>", update_todo, name="update-task"),
]