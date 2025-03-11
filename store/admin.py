from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from .models import Item
from inventory.models import Inventory
from coin.models import Coin

class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "refund_link")
    search_fields = ("name", "category")
    list_filter = ("category",)
    ordering = ("price",)

    def refund_link(self, obj):
        # 환불 버튼을 누르면 해당 Item에 대한 refund_view로 이동
        url = reverse("admin:store_item_refund", args=[obj.id])
        return format_html('<a href="{}" class="button">환불</a>', url)
    refund_link.short_description = "관리자 환불"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:item_id>/refund/',
                self.admin_site.admin_view(self.refund_view),
                name='store_item_refund'
            ),
        ]
        return urls + custom_urls

    def refund_view(self, request, item_id):
        """
        관리자가 특정 Item에 대해, 특정 유저의 Inventory에서 해당 아이템을
        부분 환불(원하는 수량만큼) 처리할 수 있는 커스텀 뷰.
        
        GET 요청: 유저 이메일과 환불 수량을 입력할 수 있는 폼 렌더링
        POST 요청: 입력된 데이터를 바탕으로 환불 처리
        """
        item = get_object_or_404(Item, id=item_id)
        if request.method == "POST":
            user_email = request.POST.get("user_email")
            refund_qty = request.POST.get("refund_qty")
            if not user_email:
                messages.error(request, "유저 이메일을 입력하세요.")
                return redirect(request.path)
            try:
                refund_qty = int(refund_qty)
            except (ValueError, TypeError):
                messages.error(request, "환불 수량은 정수여야 합니다.")
                return redirect(request.path)
            if refund_qty < 1:
                messages.error(request, "환불 수량은 1 이상이어야 합니다.")
                return redirect(request.path)
            # 유저 조회 (CustomUser는 get_user_model()로 불러옴)
            User = get_user_model()
            user = get_object_or_404(User, email=user_email)
            inventory = get_object_or_404(Inventory, user=user)
            current_qty = inventory.purchased_items.get(item.name, 0)
            if refund_qty > current_qty:
                messages.error(request, f"환불 수량({refund_qty})이 보유 수량({current_qty})보다 많습니다.")
                return redirect(request.path)
            # Inventory 모델의 refund_item 메서드 호출 (부분 환불)
            success, refund_message = inventory.refund_item(item.name, quantity=refund_qty)
            if success:
                messages.success(
                    request,
                    f"{user.nickname or user.email}의 {item.name} {refund_qty}개 환불 완료. {refund_message}"
                )
            else:
                messages.error(request, refund_message)
            return redirect(reverse("admin:store_item_changelist"))
        else:
            csrf_token = get_token(request)
            form_html = f"""
            <h2>{item.name} 환불 처리</h2>
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <label for="user_email">유저 이메일:</label>
                <input type="email" id="user_email" name="user_email" required>
                <br><br>
                <label for="refund_qty">환불 수량:</label>
                <input type="number" id="refund_qty" name="refund_qty" min="1" required>
                <br><br>
                <button type="submit" class="button">환불 처리</button>
            </form>
            """
            return HttpResponse(form_html)

admin.site.register(Item, ItemAdmin)
