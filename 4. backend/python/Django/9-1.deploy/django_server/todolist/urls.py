from django.urls import path

from .views import select_todolist, update_todo, delete_todo

# http://locahost:8000/*
urlpatterns = [
    # http://locahost:8000/
    path("", select_todolist, name="todolist"),
    # http://locahost:8000/update/id
    path("update/<int:id>", update_todo, name="update-task"),
    # http://locahost:8000/delete/id
    path("delete/<int:id>", delete_todo, name="delete-task"),
]
