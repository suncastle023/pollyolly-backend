from django.contrib import admin
from .models import Item
from inventory.models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("user", "feed", "water", "toy")  # ✅ 관리자에서 보이는 필드
    search_fields = ("user__email",)  # ✅ 사용자 이메일 검색 가능
    list_filter = ("user",)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "item_type", "created_at")  # ✅ 아이템 정보 표시
    search_fields = ("name",)
    list_filter = ("item_type", "created_at")
    ordering = ("-created_at",)
