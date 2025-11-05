from django.shortcuts import render, redirect
from django.contrib import messages

from .models import todo
# Create your views here.

def todo_list(request):
    ########################################
    # 사용자의 todo 저장 요청 
    ########################################
    if request.method == "POST":
        # 요청 코드 
        todo_task = request.POST.get("task")
        todo_task = todo_task.strip() # 빈칸 제거 코드

        # 이미지 해당 todo_task 저장되었는지 확인 
        # 없으면, 저장 & 있으면, 생략(조회)
        todo_from_db = todo.objects.filter(todo_name=todo_task)
        
        if not len(todo_task):
            messages.error(request, f"Error, task name's length: {len(todo_task)}") # 오류 발생 
            return redirect("todolist")
        elif todo_from_db:
            messages.error(request, f"Error, {todo_task} is aleady exited.") # 오류 발생 
            return redirect("todolist")
        else: # 저장하는 코드
            new_todo = todo(todo_name=todo_task)
            new_todo.save() # insert & update 

    ########################################
    # 사용자의 todo 조회 요청 
    ########################################
    # select * from todolist_todo;
    all_todos = todo.objects.all() # todo 테이블 데이터 전체 조회 

    context = {
        "todos": all_todos
    }

    return render(request, "todolist/todo.html", context)

def delete_task(request, todo_id):
    get_todo = todo.objects.get(id=todo_id) 
    get_todo.delete()
    return redirect("todolist")


def update_task(request, todo_id):
    get_todo = todo.objects.get(id=todo_id) 
    get_todo.status = True
    get_todo.save()
    return redirect("todolist") 
