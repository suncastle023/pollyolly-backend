from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from inventory.models import Inventory
from coin.models import Coin
from store.models import Item  

@login_required
def buy_item(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user
        item_name = data.get("item") 
        quantity = data.get("quantity", 1)  # 기본값 1
        
        if not item_name:
            return JsonResponse({"error": "아이템을 선택하세요"}, status=400)

        item = get_object_or_404(Item, name=item_name)  # 아이템을 데이터베이스에서 가져옴
        coin = get_object_or_404(Coin, user=user)
        inventory = get_object_or_404(Inventory, user=user)

        total_price = item.price * quantity
        if coin.amount < total_price:
            return JsonResponse({"error": "코인이 부족합니다"}, status=400)

        # 코인 차감
        coin.amount -= total_price
        coin.save()

        # 인벤토리에 아이템 추가
        success, message = inventory.add_item(item, quantity)

        if success:
            return JsonResponse({
                "message": message,
                "remaining_coins": coin.amount,
                "inventory": inventory.get_inventory_status()  # 인벤토리 상태 반환
            })
        return JsonResponse({"error": message}, status=400)

    return JsonResponse({"error": "잘못된 요청입니다"}, status=400)


@login_required
def get_items(request):
    """
    ✅ 모든 아이템 목록을 반환하는 API
    """
    items = Item.objects.all().values("name", "category", "price")
    return JsonResponse(list(items), safe=False)
