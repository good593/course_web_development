from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import todo

# 조회 및 추가
@login_required(login_url='user/login/')
def todolist(request):
    # 추가
    if request.method == 'POST':
        task = request.POST.get('task').strip()
        
        # 중복 체크
        if todo.objects.filter(user=request.user, todo_name=task).exists():
            messages.error(request, '이미 추가된 할 일입니다.')
            return redirect('todolist-todolist')
        
        elif not len(task):
            messages.error(request, '할 일을 입력하세요.')
            return redirect('todolist-todolist')
        
        new_task = todo(user=request.user, todo_name=task)
        new_task.save()
        messages.success(request, '할 일이 추가되었습니다.')
    
    # 조회
    todo_all = todo.objects.filter(user=request.user)
    context = {
        'todo_all': todo_all,
    }
    return render(request, 'todolist/todolist.html', context)

# 수정
@login_required(login_url='user/login/')
def update(request, todo_id):
    todo.objects.filter(user=request.user, id=todo_id).update(status=True)
    messages.success(request, '할 일이 완료되었습니다.')
    
    return redirect('todolist-todolist')

# 삭제
@login_required(login_url='user/login/')
def delete(request, todo_id):
    todo.objects.filter(user=request.user, id=todo_id).delete()
    messages.success(request, '할 일이 삭제되었습니다.')
    
    return redirect('todolist-todolist')
