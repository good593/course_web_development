from django.urls import path
from .views import todolist, update, delete

urlpatterns = [
    path('', todolist, name='todolist-todolist'),
    path('update/<int:todo_id>', update, name='todolist-update'),
    path('delete/<int:todo_id>', delete, name='todolist-delete'),
]
