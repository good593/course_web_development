from django.urls import path 

from .views import (
    SelectTaskList, GetTaskDetail,
    DeleteTask, InsertTask, UpdateTask
)

# http://localhost:8000/*
urlpatterns = [
    # http://localhost:8000/
    path("", SelectTaskList.as_view(), name="task-list"),
    # http://localhost:8000/task-create/
    path("task-create/", InsertTask.as_view(), name="task-create"),
    # http://localhost:8000/task-detail/pk
    path("task-detail/<int:pk>", GetTaskDetail.as_view(), name="task-detail"),
    # http://localhost:8000/task-update/pk
    path("task-update/<int:pk>", UpdateTask.as_view(), name="task-update"),
    # http://localhost:8000/task-delete/pk
    path("task-delete/<int:pk>", DeleteTask.as_view(), name="task-delete"),
]
