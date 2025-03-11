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
        try:
            data = json.loads(request.body)
            user = request.user
            user_display_name = user.nickname or user.email  # ✅ 닉네임이 없으면 이메일 사용
            item_name = data.get("item_name")
            quantity = data.get("quantity", 1)  # 기본값 1

            if not item_name:
                return JsonResponse({"error": "아이템을 선택하세요"}, status=400)

            item = get_object_or_404(Item, name=item_name)  # 아이템 가져오기
            coin = get_object_or_404(Coin, user=user)  # 유저 코인 가져오기
            inventory, created = Inventory.objects.get_or_create(user=user)  # 인벤토리 가져오기 (없으면 생성)

            # ✅ 새 인벤토리가 생성된 경우 초기 설정 (예: 기본 아이템 지급)
            if created:
                print(f"[새 인벤토리 생성] {user_display_name}의 인벤토리 초기화 완료")
                inventory.feed = 5
                inventory.water = 5
                inventory.save()

            print(f"🔹 [구매 요청] 유저: {user_display_name}, 아이템: {item_name}, 개수: {quantity}")
            print(f"🔹 [잔여 코인] {coin.amount} → 필요 코인: {item.price * quantity}")

            total_price = item.price * quantity
            if coin.amount < total_price:
                return JsonResponse({"error": "코인이 부족합니다"}, status=400)

            # ✅ 코인 차감
            coin.amount -= total_price
            coin.save()

            success, message = inventory.buy_item(item_name, coin, quantity)

            if success:
                print(f"✅ [구매 완료] {item_name} {quantity}개")
                return JsonResponse({
                    "message": message,
                    "remaining_coins": coin.amount,
                    "inventory": inventory.get_inventory_status()  # ✅ 인벤토리 상태 반환
                })
            return JsonResponse({"error": message}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다"}, status=400)
        except Exception as e:
            print(f"❌ [오류 발생] {str(e)}")
            return JsonResponse({"error": f"서버 오류: {str(e)}"}, status=500)

    return JsonResponse({"error": "잘못된 요청입니다"}, status=400)


#아이템 목록 반환 api
@login_required
def get_items(request):
    items = Item.objects.all().values("name", "category", "price")
    return JsonResponse(list(items), safe=False)
