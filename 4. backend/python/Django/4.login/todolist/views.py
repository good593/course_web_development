from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import todo

# Create your views here.
@login_required(login_url="/user/login/")
def search_todolist(request):
    """
    첫번째(get): todolist 조회 
    두번째(post): todo 추가
    검증
    - 이미 등록된 todo는 추가 불가 
    - 로그인 하지 않은 사람 접속 불가  
    """
    if request.method == "POST":
        # todo 저장 
        task = request.POST.get("task").strip()
        is_task = todo.objects.filter(
            user=request.user, todo_name=task
        )
        if is_task:
            messages.error(request, f"[에러] {task}가 이미 존재합니다.")
            return redirect("todolist")

        new_todo = todo(user=request.user, todo_name=task)
        new_todo.save()


    # todolist 조회 
    todolist_by_user = todo.objects.filter(
        user=request.user
    )
    return render(
        request, "todolist/todo.html",
        {
            "todos":todolist_by_user
        }
    )

@login_required(login_url="/user/login/")
def delete_todo(request, id):
    get_todo = todo.objects.get(user=request.user, id=id) 
    get_todo.delete()
    return redirect("todolist")

@login_required(login_url="/user/login/")
def update_todo(request, id):
    get_todo = todo.objects.get(user=request.user, id=id) 
    get_todo.status = True
    get_todo.save()
    return redirect("todolist") 

