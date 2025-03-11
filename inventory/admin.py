from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
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

    def refund_action(self, obj):
        return format_html(
            '<a href="/admin/inventory/{}/refund/" class="button">환불</a>',
            obj.id
        )

    refund_action.short_description = "환불"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:inventory_id>/refund/', self.admin_site.admin_view(self.refund_selected_items)),
        ]
        return custom_urls + urls

    def refund_selected_items(self, request, inventory_id):
        inventory = Inventory.objects.get(id=inventory_id)
        refunded_count = 0

        for item_name in list(inventory.purchased_items.keys()):
            success, _ = inventory.refund_item(item_name)
            if success:
                refunded_count += 1

        messages.success(request, f"{refunded_count}개 아이템이 환불되었습니다.")
        return redirect("..")

admin.site.register(Inventory, InventoryAdmin)
