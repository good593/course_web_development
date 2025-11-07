from django.shortcuts import render, redirect 
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib import messages

from .models import Task 
from .forms import TaskForm

# Create your views here.
class SelectTaskList(TemplateView):
    template_name = "todolist/task_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_input = self.request.GET.get("search-area", "")
        if search_input:
            context['taskList'] = Task.objects.filter(
                custom=self.request.user, title__startswith=search_input)
        else:
            context['taskList'] = Task.objects.filter(custom=self.request.user)

        context['search_input'] = search_input
        context['cnt'] = Task.objects.filter(
            custom=self.request.user, complete=False).count()
        return context 

class GetTaskDetail(TemplateView):
    template_name = "todolist/task_detail.html"

    def get_context_data(self, pk):
        context = super().get_context_data()
        one_task = Task.objects.get(id=pk, custom=self.request.user)
        context['form'] = TaskForm(instance=one_task)
        context['task'] = one_task
        return context

class InsertTask(TemplateView):
    template_name = "todolist/task_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TaskForm()
        return context 

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():                 # 검증 성공!!
            task = form.save(commit=False)  # 아직 저장하지마...
            task.custom = request.user      # 등록하는 유저 추가 
            task.save()                     # DB에 저장!!
            return redirect("task-list")

        # 검증 실패!!
        messages.error(request, form.errors)
        return redirect("task-create")

class UpdateTask(TemplateView):
    template_name = "todolist/task_form.html"

    def get_context_data(self, pk):
        context = super().get_context_data()
        get_task = Task.objects.get(id=pk, custom=self.request.user)
        context['form'] = TaskForm(instance=get_task)
        context['task'] = get_task
        return context

    def post(self, request, pk):
        # 기존 데이터 조회 
        get_task = Task.objects.get(id=pk, custom=self.request.user)
        # 기존 데이터에 수정(웹에서 받은 데이터를 추가/변경)
        form = TaskForm(request.POST, instance=get_task)
        if form.is_valid():                 # 검증 성공!!
            task = form.save(commit=False)  # 아직 저장하지마...
            task.custom = request.user      # 등록하는 유저 추가 
            task.save()                     # DB에 저장!!
            return redirect("task-list")

        # 검증 실패!!
        messages.error(request, form.errors)
        return redirect("task-create")

class DeleteTask(TemplateView):
    template_name = "todolist/task_delete.html"

    def get_context_data(self, pk):
        context = super().get_context_data()
        context['task'] = Task.objects.get(id=pk, custom=self.request.user)
        return context

    def post(self, request, pk):
        get_task = Task.objects.get(id=pk, custom=request.user)
        get_task.delete()
        return redirect("task-list")
