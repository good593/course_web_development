from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views import View
from django.contrib import messages

from .models import todo

# Create your views here.
class Search_TodoList(TemplateView):
    template_name = "todolist/todo.html"
    login_url = "user-login"  # 로그인 안 되어 있으면 이 URL로 이동

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["todos"] = todo.objects.filter(
            user=self.request.user
        )
        return context

    def post(self, request):
        task = request.POST.get("task").strip()
        is_task = todo.objects.filter(
            user=request.user, todo_name=task
        )
        if is_task:
            messages.error(request, f"[에러] {task}가 이미 존재합니다.")
            return redirect("todolist")

        new_todo = todo(user=request.user, todo_name=task)
        new_todo.save() 
        return redirect("todolist")

class Delete_Todo(View):
    def get(self, request, id):
        get_todo = todo.objects.get(user=request.user, id=id) 
        get_todo.delete()
        return redirect("todolist")

class Update_Todo(View):
    def get(self, request, id):
        get_todo = todo.objects.get(user=request.user, id=id) 
        get_todo.status = True
        get_todo.save()
        return redirect("todolist")
