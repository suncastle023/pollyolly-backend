from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.shortcuts import get_object_or_404
from .models import Item
from inventory.models import Inventory
from coin.models import Coin

class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "refund_link")
    search_fields = ("name", "category")
    list_filter = ("category",)
    ordering = ("price",)

    # 개별 환불 버튼: 해당 아이템의 id를 인자로 custom view 호출
    def refund_link(self, obj):
        url = reverse("admin:refund_all_view", args=[obj.id])
        return format_html('<a href="{}" class="button">환불</a>', url)
    refund_link.short_description = "관리자 환불"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:item_id>/refund_all/', self.admin_site.admin_view(self.refund_all_view), name='refund_all_view'),
        ]
        return custom_urls + urls

    def refund_all_view(self, request, item_id):
        """
        해당 아이템을 구매한 모든 사용자의 인벤토리에서
        구매 내역(purchased_items)에서 해당 아이템을 제거하고, 
        그에 상응하는 코인을 환불하는 관리자 전용 뷰.
        """
        item = get_object_or_404(Item, id=item_id)
        refunded_count = 0
        # 구매 내역에 해당 아이템이 기록된 모든 Inventory에 대해 환불 진행
        for inventory in Inventory.objects.filter(purchased_items__has_key=item.name):
            quantity = inventory.purchased_items.get(item.name, 0)
            if quantity > 0:
                coin = Coin.objects.get(user=inventory.user)
                refund_amount = item.price * quantity
                coin.amount += refund_amount
                coin.save()
                del inventory.purchased_items[item.name]
                inventory.save()
                refunded_count += 1
        self.message_user(request, f"{refunded_count}개 인벤토리에서 {item.name} 환불 완료.")
        # 현재 Item list 페이지로 돌아감
        return HttpResponseRedirect("../")

    # bulk 환불 액션 (여러 아이템 선택 시 환불)
    actions = ["refund_selected_items"]

    def refund_selected_items(self, request, queryset):
        refunded_count = 0
        for item in queryset:
            for inventory in Inventory.objects.filter(purchased_items__has_key=item.name):
                quantity = inventory.purchased_items.get(item.name, 0)
                if quantity > 0:
                    coin = Coin.objects.get(user=inventory.user)
                    refund_amount = item.price * quantity
                    coin.amount += refund_amount
                    coin.save()
                    del inventory.purchased_items[item.name]
                    inventory.save()
                    refunded_count += 1
        self.message_user(request, f"{refunded_count}개 인벤토리에서 선택된 아이템 환불 완료.")
        return HttpResponseRedirect(request.get_full_path())

    refund_selected_items.short_description = "선택된 아이템 환불"

admin.site.register(Item, ItemAdmin)
