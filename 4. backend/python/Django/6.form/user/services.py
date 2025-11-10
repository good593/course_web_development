from django.contrib.auth import authenticate

from .models import CustomUser

def user_by_valid_login(name, password):
    # name 검증 -> 데이터베이스 해당 name 유무 확인 
    if not CustomUser.objects.filter(name=name).exists():
        raise ValueError(f"{name}는 존재하지 않는 사용자입니다.")
    
    # password 검증
    is_user = authenticate(username=name, password=password)
    if not is_user:
        raise ValueError(f"입력한 비밀번호가 올바르지 않습니다.")
   
    return is_user
