from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("user", "feed", "water", "toy", "last_fed", "last_water")
    list_filter = ("last_fed", "last_water")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("last_fed", "last_water")

    # ✅ 관리자가 인벤토리 아이템 개수를 직접 수정할 수 있도록 설정
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []  # 슈퍼유저는 모든 필드를 수정 가능
        return self.readonly_fields


