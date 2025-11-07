from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Create your models here.
class CustomUserManager(BaseUserManager):
    """ORM을 적용하기 위한 클래스"""
    use_in_migrations  = True # python manage.py makeimgrations

    def is_valid(self, name, password, email):
        if not name:
            raise ValueError("이름(name)은 필수 항목입니다.")
        if not email:
            raise ValueError("이메일(email)은 필수 항목입니다.")
        if not password:
            raise ValueError("비밀번호(password)는 필수 항목입니다.")

        # --- 이메일 형식 검증 ---
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("올바른 이메일 형식이 아닙니다.")

        # --- 중복 확인 ---
        if self.model.objects.filter(name=name).exists():
            raise ValueError(f"이미 존재하는 사용자명입니다: {name}")
        if self.model.objects.filter(email=email).exists():
            raise ValueError(f"이미 존재하는 이메일입니다: {email}")

        # --- 비밀번호 검증 ---
        if len(password) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")

        # 모든 검증 통과
        return True

    def create_user(self, name, password, email):
        """일반 유저 생성"""
        self.is_valid(name, password, email)
        
        user = self.model(
            email = self.normalize_email(email),
            name = name
        )
        user.set_password(password) # 비밀번호 암호화 
        user.save(using=self._db)   # 새로운 계정 저장 
        return user 


    def create_superuser(self, name, password, email):
        """관리자 유저 생성"""
        user = self.create_user(name, password, email)

        user.is_admin = True 
        user.is_superuser = True
        user.save(using=self._db)   # 권한 업데이트 진행 
        return user  


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    DB에 생성될 테이블 정보
    [중요] settings.py에 추가해야함 
        AUTH_USER_MODEL = "user.CustomUser" # 커스텀 사용자 클래스 정의
    """
    objects = CustomUserManager()

    email = models.EmailField(max_length=500, unique=True, null=False)
    name = models.CharField(max_length=100, unique=True, null=False)
    
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custom' # 생성될 테이블명 

    # 로그인할 때, 사용할 id컬럼
    USERNAME_FIELD = 'name'
    # 가입할 때, 필수로 받아야할 컬럼리스트 
    REQUIRED_FIELDS = ['email'] 

