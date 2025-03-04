from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.sessions.models import Session
from django.utils.timezone import now

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



class SessionAdmin(admin.ModelAdmin):
    list_display = ("session_key", "user", "expire_date")
    ordering = ("-expire_date",)

    def user(self, obj):
        """세션에서 사용자 ID를 추출하여 CustomUser 모델에서 조회"""
        data = obj.get_decoded()
        user_id = data.get("_auth_user_id")
        if user_id:
            return CustomUser.objects.filter(id=user_id).first()
        return None

    def get_queryset(self, request):
        """만료되지 않은 세션만 표시"""
        qs = super().get_queryset(request)
        return qs.filter(expire_date__gte=now())

admin.site.register(Session, SessionAdmin)
