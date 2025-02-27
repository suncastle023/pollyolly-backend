from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'nickname', 'phone_number']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def validate(self, data):
        if "password" in data and data['password'] != data.get('password2'):
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})

        if User.objects.filter(nickname=data['nickname']).exists():
            raise serializers.ValidationError({"nickname": "이미 사용 중인 닉네임입니다."})

        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password', None)

        if password:
            user = User.objects.create_user(**validated_data, password=password)  # 일반 로그인
        else:
            user = User.objects.create_user(**validated_data)  # 카카오 로그인 사용자 (비밀번호 없음)

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
