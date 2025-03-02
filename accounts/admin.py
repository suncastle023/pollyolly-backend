from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "nickname", "level", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "nickname")
    ordering = ("email",)
    fieldsets = (
        ("기본 정보", {"fields": ("email", "password", "nickname", "phone_number", "kakao_id")}),
        ("레벨 및 상태", {"fields": ("level", "is_active", "is_staff", "is_superuser")}),
        ("권한 설정", {"fields": ("groups", "user_permissions")}),
        ("중요한 날짜", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        ("새 사용자 추가", {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "nickname", "phone_number", "is_active", "is_staff"),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
