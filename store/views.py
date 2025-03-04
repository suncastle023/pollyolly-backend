from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from inventory.models import Inventory
from coin.models import Coin

@csrf_exempt
def buy_item(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user
        item_type = data.get("item")

        if not item_type:
            return JsonResponse({"error": "아이템을 선택하세요"}, status=400)

        coin = get_object_or_404(Coin, user=user)
        inventory = get_object_or_404(Inventory, user=user)

        success, message = inventory.buy_item(item_type, coin)

        if success:
            return JsonResponse({
                "message": message,
                "remaining_coins": coin.amount,
                "inventory": {
                    "feed": inventory.feed,
                    "toy": inventory.toy,
                    "water": inventory.water
                }
            })
        return JsonResponse({"error": message}, status=400)

    return JsonResponse({"error": "잘못된 요청입니다"}, status=400)
