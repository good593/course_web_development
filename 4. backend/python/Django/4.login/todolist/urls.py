from django.urls import path
from .views import todo_list, delete_task, update_task

# localhost
urlpatterns = [
    # localhost
    path("", todo_list, name="todo-list"),
    # localhost/delete-task/task
    path("delete-task/<str:task>", delete_task, name="delete-task"),
    # localhost/update-task/task
    path("update-task/<str:task>", update_task, name="update-task"),
]
