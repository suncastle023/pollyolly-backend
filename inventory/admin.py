from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("user", "feed", "pm_feed", "water", "pm_water", "toy1", "toy2", "toy3", "display_purchased_items", "last_fed", "last_water")
    list_filter = ("last_fed", "last_water")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("last_fed", "last_water", "display_purchased_items")

    # ✅ 구매한 아이템 JSONField를 Admin에서 보기 쉽게 변환
    def display_purchased_items(self, obj):
        if obj.purchased_items:
            return ", ".join([f"{key}: {value}개" for key, value in obj.purchased_items.items()])
        return "구매한 아이템 없음"
    
    display_purchased_items.short_description = "구매한 아이템 목록"

    # ✅ 관리자가 인벤토리 아이템 개수를 직접 수정할 수 있도록 설정
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []  # 슈퍼유저는 모든 필드를 수정 가능
        return self.readonly_fields
