from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.middleware.csrf import get_token
from .models import Inventory

class InventoryAdmin(admin.ModelAdmin):
    list_display = ("user_email", "user_nickname", "display_purchased_items", "refund_actions")
    search_fields = ("user__email", "user__nickname")

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "이메일"

    def user_nickname(self, obj):
        return obj.user.nickname or "닉네임 없음"
    user_nickname.short_description = "닉네임"

    def display_purchased_items(self, obj):
        if obj.purchased_items:
            return ", ".join([f"{item}: {qty}개" for item, qty in obj.purchased_items.items()])
        return "구매한 아이템 없음"
    display_purchased_items.short_description = "구매한 아이템"

    def refund_actions(self, obj):
        """
        각 인벤토리 내 구매한 아이템마다 환불 버튼을 생성합니다.
        버튼 클릭 시, 해당 아이템에 대해 환불 수량을 입력하는 폼으로 이동합니다.
        """
        if not obj.purchased_items:
            return "환불 없음"
        links = []
        for item_name, qty in obj.purchased_items.items():
            url = reverse("admin:refund_inventory_item", args=[obj.id, item_name])
            links.append(f'<a href="{url}" class="button">[{item_name}] 환불</a>')
        return format_html(" ".join(links))
    refund_actions.short_description = "환불 액션"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:inventory_id>/refund/<str:item_name>/',
                self.admin_site.admin_view(self.refund_inventory_item),
                name='refund_inventory_item'
            ),
        ]
        return custom_urls + urls

    def refund_inventory_item(self, request, inventory_id, item_name):
        """
        해당 인벤토리(유저)의 purchased_items에서 item_name에 해당하는 아이템을 환불합니다.
        GET: 현재 보유 수량을 보여주는 폼을 렌더링
        POST: 입력한 환불 수량만큼 환불 진행
        """
        inventory = get_object_or_404(Inventory, id=inventory_id)
        current_quantity = inventory.purchased_items.get(item_name)
        if not current_quantity:
            messages.error(request, "환불할 아이템이 없습니다.")
            return redirect("..")
        
        if request.method == "POST":
            refund_qty = request.POST.get("refund_qty")
            try:
                refund_qty = int(refund_qty)
            except (ValueError, TypeError):
                messages.error(request, "환불 수량은 정수여야 합니다.")
                return redirect(request.path)
            if refund_qty < 1:
                messages.error(request, "환불 수량은 1 이상이어야 합니다.")
                return redirect(request.path)
            if refund_qty > current_quantity:
                messages.error(request, f"환불 수량({refund_qty})이 보유 수량({current_quantity})보다 많습니다.")
                return redirect(request.path)
            
            success, message_text = inventory.refund_item(item_name, quantity=refund_qty)
            if success:
                messages.success(
                    request, 
                    f"{inventory.user.nickname or inventory.user.email}의 {item_name} {refund_qty}개 환불 완료. (환불 금액: {int(message_text.split()[-2])} 코인)"
                )
            else:
                messages.error(request, message_text)
            return redirect("..")
        else:
            csrf_token = get_token(request)
            form_html = f"""
            <h2>{inventory.user.nickname or inventory.user.email}의 {item_name} 환불</h2>
            <p>보유 수량: {current_quantity}개</p>
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <label for="refund_qty">환불 수량:</label>
                <input type="number" id="refund_qty" name="refund_qty" min="1" max="{current_quantity}" value="1">
                <button type="submit" class="button">환불하기</button>
            </form>
            """
            return HttpResponse(form_html)

admin.site.register(Inventory, InventoryAdmin)
