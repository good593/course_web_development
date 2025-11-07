from rest_framework.serializers import ModelSerializer
from .models import User

# api통신때 user정보를 제공하기 위한 객체 
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {
            # 쓰기 전용이기 때문에 비번은 api통신 때 리턴되지 않음 
            'password': {'write_only': True}
        }

    # user 생성 요청이 들어올 때, 비밀번호가 hashing 처리된 후 db에 저장 
    def create(self, validated_data):
        print("[UserSerializer][create] Start")
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            # provide django, password will be hashing!
            instance.set_password(password)
        instance.save()
        return instance
    