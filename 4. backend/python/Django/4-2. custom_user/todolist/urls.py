from django.urls import path 

from .views import (
    Search_TodoList, Delete_Todo, Update_Todo
)

urlpatterns = [
    path("", Search_TodoList.as_view(), name="todolist"),
    path("delete/<int:id>/", Delete_Todo.as_view(), name="delete-task"),
    path("update/<int:id>/", Update_Todo.as_view(), name="update-task"),
]
