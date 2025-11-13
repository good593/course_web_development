from django.shortcuts import render, redirect
from django.contrib import messages

from .services import insert_todo, select_todos, get_todo

# Create your views here.
def select_todolist(request):
    try:
        # 저장
        if request.method == "POST":
            todo_name = request.POST.get("task").strip()
            insert_todo(todo_name, request.user) 

        # 조회
        return render(
            request, "todolist/todo.html",
            {
                "todos": select_todos(request.user)
            }
        )
    except Exception as e:
        messages.error(request, str(e))
        return redirect("todolist") 

def update_todo(request, id):
    todo = get_todo(request.user, id)
    todo.status = True 
    todo.save()
    return redirect("todolist") 

def delete_todo(request, id):
    todo = get_todo(request.user, id)
    todo.delete()
    return redirect("todolist") 

