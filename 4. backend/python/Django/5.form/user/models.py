from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db import models 

# https://hckcksrl.medium.com/django-%EC%BB%A4%EC%8A%A4%ED%85%80-%EC%9C%A0%EC%A0%80-%EB%AA%A8%EB%8D%B8-custom-user-model-b8487c0d150
# https://www.coninggu.com/8
# https://blaize.tistory.com/89

# 유저를 생성할 때, 사용하는 클래스
class CustomManager(BaseUserManager):    
    
    use_in_migrations = True    
    
    def create_user(self, name, password=None, email=None):        
        
        if not email :            
            raise ValueError('must have user email')        
        user = self.model(            
            email = self.normalize_email(email),            
            name = name        
        )        
        user.set_password(password)        
        user.save(using=self._db)        
        return user     
    def create_superuser(self, name, password, email=None ):        
    
        user = self.create_user(            
            email = self.normalize_email(email),            
            name = name,            
            password=password        
        )        
        user.is_admin = True        
        user.is_superuser = True        
        user.save(using=self._db)        
        return user 


# 유저 모델(테이블, 객체)
class Custom(AbstractBaseUser,PermissionsMixin):  
    objects = CustomManager()

    email = models.EmailField(
        max_length=255, 
        unique=True, null=False
    )
    name = models.CharField(
        max_length=20, 
        unique=True, null=False
    ) 
    is_superuser = models.BooleanField(default=False)    
    s_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custom'

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']

