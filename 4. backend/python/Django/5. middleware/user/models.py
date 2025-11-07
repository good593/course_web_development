from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Create your models here.
class CustomUserManager(BaseUserManager):
    """ORM을 적용하기 위한 클래스"""
    use_in_migrations = True 

    def is_valid(self, name, password, email):
        """검증 로직"""
        if not name:
            raise ValueError("name은 필수 항목입니다.")
        elif (not password) or (len(password) < 5):
            raise ValueError("password는 필수 항목이면서, 최소 길이는 5이상입니다.")
        
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("올바른 이메일 형식이 아닙니다.")

        if self.model.objects.filter(name=name).exists():
            raise ValueError(f"{name}은 이미 존재하는 사용자명입니다.")
        elif self.model.objects.filter(email=email).exists():
            raise ValueError(f"{email}은 이미 존재하는 이메일입니다.")

        return True # 모든 검증 통과 


    def create_user(self, name, password, email):
        """일반 유저 생성"""
        self.is_valid(name, password, email) # 검증 

        user = self.model(
            name = name ,
            email = self.normalize_email(email)
        ) # 새로운 계정 생성 
        user.set_password(password) # 비밀번호 암호화 
        user.save(using=self._db)   # 새로운 계정 저장
        return user 

    def create_superuser(self, name, password, email):
        """관리자 유저 생성"""
        user = self.create_user(name, password, email) # 새로운 유저 생성 

        user.is_admin = True 
        user.is_superuser = True 
        user.save(using=self._db)   # 수정된 내용 업데이트 
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    DB에 생성될 테이블 정보(스키마)
    [중요] setting.py에 설정 
        AUTH_USER_MODEL = "user.CustomUser"
    """
    objects = CustomUserManager()

    name = models.CharField(max_length=100, unique=True, null=False)
    email = models.EmailField(max_length=500, unique=True, null=False)

    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customUser' # 생성될 테이블명 

    # 필수 & 유니크
    USERNAME_FIELD = 'name'  

    # 가입할 때, 추가적으로 필수로 받아야할 컬럼 리스트 
    REQUIRED_FIELDS = ['email']
