from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("user_email", "user_nickname", "feed", "pm_feed", "water", "pm_water", "toy1", "toy2", "toy3", "display_purchased_items", "last_fed", "last_water")
    list_filter = ("last_fed", "last_water")
    search_fields = ("user__email", "user__nickname")
    readonly_fields = ("last_fed", "last_water", "display_purchased_items")

    def user_email(self, obj):
        return obj.user.email

    def user_nickname(self, obj):
        return obj.user.nickname or "닉네임 없음"

    user_email.short_description = "이메일"
    user_nickname.short_description = "닉네임"

    def display_purchased_items(self, obj):
        if obj.purchased_items:
            return ", ".join([f"{key}: {value}개" for key, value in obj.purchased_items.items()])
        return "구매한 아이템 없음"
    
    display_purchased_items.short_description = "구매한 아이템 목록"

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []  # 슈퍼유저는 모든 필드를 수정 가능
        return self.readonly_fields
