from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.contrib import messages

from .forms import TaskForm
from .services import (
    select_tasks, 
    count_not_completed_tasks,
    get_task, delete_task
)

# task 리스트 조회 화면 
class SelectTaskList(TemplateView):
    template_name = "todolist/task_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 사용자의 입력 데이터 
        context['search_input'] = self.request.GET.get("search-area", "")
        # 사용자가 등록한 task list 조회 
        context['taskList'] = select_tasks(
            custom=self.request.user, 
            search_input=context['search_input']
        )
        # 사용자가 등록한 task list 중 완료가 되지 않은 수 
        context['cnt'] = count_not_completed_tasks(
            custom=self.request.user
        )
        
        return context

# (하나의) task 상세 화면 
class GetTaskDetail(TemplateView):
    template_name = "todolist/task_detail.html"

    def get_context_data(self, pk):
        context = super().get_context_data()
        context['task'] = get_task(
            custom=self.request.user, id=pk
        )
        context['form'] = TaskForm(instance=context['task'])

        return context

# task 삭제 화면
class DeleteTask(TemplateView):
    template_name = "todolist/task_delete.html"

    def get_context_data(self, pk):
        context = super().get_context_data()
        context['task'] = get_task(
            custom=self.request.user, id=pk
        )
        return context

    def post(self, request, pk):
        if not delete_task(
            custom=self.request.user, id=pk
        ):
            messages.error(request, f"알수없는 오류 발생으로 인해, 요청하신 task 삭제하지 못했습니다.")
            
        return redirect("task-list")

# task 추가 화면
class InsertTask(TemplateView):
    template_name = "todolist/task_form.html"

    def get_context_data(self):
        context = super().get_context_data()
        context['form'] = TaskForm()
        return context 

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():                 # 검증성공 
            task = form.save(commit=False)  # 아직 저장전...
            task.custom = request.user      # 등록 유저 정보 추가..
            task.save()                     # 데이터베이스에 저장 
            return redirect("task-list")

        messages.error(request, form.errors)
        return redirect("task-create")
             
# task 수정 화면 
class UpdateTask(TemplateView):
    template_name = "todolist/task_form.html"

    def get_context_data(self, pk):
        context = super().get_context_data()
        context['task'] = get_task(
            custom=self.request.user, id=pk
        )
        context['form'] = TaskForm(instance=context['task'])
        return context 

    def post(self, request, pk):
        one_task = get_task(
            custom=self.request.user, id=pk
        )

        form = TaskForm(request.POST, instance=one_task)
        if form.is_valid():                 # 검증성공 
            task = form.save(commit=False)  # 아직 저장전...
            task.custom = request.user      # 등록 유저 정보 추가..
            task.save()                     # 데이터베이스에 저장 
            return redirect("task-list")

        messages.error(request, form.errors)
        return redirect("task-create")

 

