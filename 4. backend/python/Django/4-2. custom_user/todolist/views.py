from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.views import View 
from django.contrib import messages

from .models import Todo

# Create your views here.
class SelectTodoList(TemplateView):
    template_name = "todolist/todo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['todos'] = Todo.objects.filter(
            user=self.request.user
        )
        return context

    def post(self, request):
        task = request.POST.get('task').strip()
        
        if Todo.objects.filter(
            user=request.user, todo_name=task
        ).exists():
            messages.error(request, f"{task}는 이미 존재합니다.")
            return redirect("todolist")
        
        new_todo = Todo(user=request.user, todo_name=task)
        new_todo.save()
        return redirect("todolist")

class DeleteTodo(View):
    def get(self, request, id):
        one_todo = Todo.objects.get(user=request.user, id=id)
        one_todo.delete()
        return redirect("todolist")

class UpdateTodo(View):
    def get(self, request, id):
        one_todo = Todo.objects.get(user=request.user, id=id)
        one_todo.status = True
        one_todo.save()
        return redirect("todolist")
