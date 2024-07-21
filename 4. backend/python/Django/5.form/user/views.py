from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomForm, CustomCreationForm

# Create your views here.
def user_login(request):
    if request.user.is_authenticated:
        return redirect("task-list")
    elif request.method == 'POST':
        name = request.POST.get("name")
        pwd = request.POST.get("password")
        validate_user = authenticate(name=name, password=pwd)
        if validate_user is not None:
            login(request, validate_user)
            return redirect('task-list')
        else:
            messages.info(request, 'Try again! username or password is incorrect')
            return redirect("login")

    template_name = 'user/login.html' 
    context={'form':CustomForm()}
    return render(request, template_name, context)  

def user_register(request):
    if request.user.is_authenticated:
        return redirect("task-list")
    elif request.method == "POST":
        form = CustomCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
        else:
            # messages.info(request, 'Try again!')
            messages.error(request, form.errors)
            return redirect("register")
    
    template_name = 'user/register.html'
    context={'form':CustomCreationForm()}
    return render(request, template_name, context)  

