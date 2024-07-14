from django.shortcuts import render, redirect
from django.contrib import messages

from .models import todo

# todo 조회 및 생성
def todo_list(request):
    if request.method == "POST":
        task = request.POST.get("task")
        todo_obj = todo.objects.filter(todo_name=task)
        if todo_obj:
            messages.error(request, f"Error, {task} is aleady exited.")
        elif not len(task):
            messages.error(request, f"Error, task name's length: {len(task)}")
        else:
            new_todo = todo(todo_name=task)
            new_todo.save()
            
    all_todos = todo.objects.all()
    context = {"todos": all_todos}
    return render(request, "todoList/todo.html", context)

# todo 삭제 
def delete_task(request, task):
    get_todo = todo.objects.get(todo_name=task)
    get_todo.delete()
    return redirect("todo-list")

# todo 수정 
def update_task(request, task):
    get_todo = todo.objects.get(todo_name=task)
    get_todo.status = True
    get_todo.save()
    return redirect("todo-list")