from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, nickname=None, kakao_id=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수 항목입니다.")
        email = self.normalize_email(email)

        if kakao_id:
            user = self.model(email=email, kakao_id=kakao_id, nickname=nickname, **extra_fields)
            user.set_unusable_password()  # 비밀번호 없이 생성
        else:
            user = self.model(email=email, nickname=nickname, **extra_fields)
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    kakao_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    nickname = models.CharField(max_length=30, unique=True, null=True, blank=True)  
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    level = models.IntegerField(default=1)  # 기본 레벨 1
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]  

    def __str__(self):
        return self.nickname or self.email

