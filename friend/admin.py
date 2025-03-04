from django.contrib import admin
from .models import Friend, FriendRequest

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ("user", "friend", "created_at")  # ✅ 관리자 페이지에서 보이는 필드
    search_fields = ("user__email", "friend__email")  # ✅ 이메일 기준 검색 가능
    list_filter = ("created_at",)  # ✅ 날짜 필터 추가
    ordering = ("-created_at",)

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("sender__email", "receiver__email")
    ordering = ("-created_at",)
