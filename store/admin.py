from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "item_type", "created_at")  # ✅ 아이템 정보 표시
    search_fields = ("name",)
    list_filter = ("item_type", "created_at")
    ordering = ("-created_at",)
