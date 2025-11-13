from .models import Task 

# task list 조회 
def select_tasks(custom, search_input:str=None):
    if search_input:
        return Task.objects.filter(
            custom=custom, title__startswith=search_input
        )

    return Task.objects.filter(
            custom=custom
        )

# 완료되지 않은 task count 조회 
def count_not_completed_tasks(custom):
    return Task.objects.filter(
            custom=custom, complete=False
        ).count()

# task 조회 
def get_task(custom, id):
    return Task.objects.get(
        id=id, custom=custom
    )

# task 삭제 
def delete_task(custom, id):
    try:
        one_task = Task.objects.get(
            id=id, custom=custom
        )
        one_task.delete() 
        return True 
    except:
        return False

