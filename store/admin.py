from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Item
from inventory.models import Inventory
from coin.models import Coin

class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "refund_link")  # ✅ 환불 기능 추가
    search_fields = ("name", "category")  # ✅ 검색 필드 추가
    list_filter = ("category",)  # ✅ 카테고리별 필터
    ordering = ("price",)  # ✅ 가격 기준 정렬

    def refund_link(self, obj):
        return format_html(
            '<a href="/admin/store/item/{}/refund/" class="button">환불</a>',
            obj.id
        )
    refund_link.short_description = "관리자 환불"

    # ✅ 환불 액션 추가
    actions = ["refund_selected_items"]

    def refund_selected_items(self, request, queryset):
        """
        ✅ 선택된 아이템을 환불하는 관리자 기능
        """
        refunded_count = 0
        for item in queryset:
            for inventory in Inventory.objects.filter(purchased_items__has_key=item.name):
                user = inventory.user
                coin = Coin.objects.get(user=user)

                # ✅ 아이템 환불
                quantity = inventory.purchased_items.get(item.name, 0)
                if quantity > 0:
                    # 코인 반환
                    refund_amount = item.price * quantity
                    coin.amount += refund_amount
                    coin.save()

                    # 인벤토리에서 아이템 제거
                    del inventory.purchased_items[item.name]
                    inventory.save()

                    refunded_count += 1

        messages.success(request, f"{refunded_count}개 아이템이 환불되었습니다.")
        return HttpResponseRedirect(request.get_full_path())

    refund_selected_items.short_description = "선택된 아이템 환불"

admin.site.register(Item, ItemAdmin)
