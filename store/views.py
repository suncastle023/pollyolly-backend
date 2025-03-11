# store/views.py
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from inventory.models import Inventory
from coin.models import Coin
from store.models import Item
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


class BuyItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_name = request.data.get("item_name")
        try:
            quantity = int(request.data.get("quantity", 1))
        except (ValueError, TypeError):
            quantity = 1

        # 기본 비즈니스 로직: Inventory의 buy_item() 호출
        coin = Coin.objects.get(user=request.user)
        inventory, _ = Inventory.objects.get_or_create(user=request.user)

        success, message = inventory.buy_item(item_name, coin, quantity)

        if success:
            return Response({
                "success": True,
                "message": message,
                "remaining_coins": coin.amount,
                "inventory": inventory.get_inventory_status()
            })
        return Response({"success": False, "message": message}, status=400)

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def refund_item_admin(request):
    """
    관리자 전용 API: 특정 유저의 특정 아이템 환불
    요청 JSON 예시:
    {
        "user_email": "test@example.com",
        "item_name": "default_bg2",
        "quantity": 1  # (옵션, 미입력 시 전체 환불)
    }
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_email = data.get("user_email")
            item_name = data.get("item_name")
            quantity = data.get("quantity")  # 선택적; 미입력 시 전체 환불

            if not user_email or not item_name:
                return JsonResponse({"error": "유저 이메일과 아이템 이름을 입력하세요."}, status=400)

            User = get_user_model()
            user = get_object_or_404(User, email=user_email)
            inventory = get_object_or_404(Inventory, user=user)

            # 환불 요청: quantity가 주어지면 정수로 변환, 없으면 None(전체 환불)
            if quantity is not None:
                try:
                    quantity = int(quantity)
                except ValueError:
                    return JsonResponse({"error": "환불 수량은 정수여야 합니다."}, status=400)

            success, message = inventory.refund_item(item_name, quantity=quantity)
            if success:
                return JsonResponse({
                    "message": f"{user.nickname or user.email}의 {item_name} 환불 완료! {message}"
                })
            return JsonResponse({"error": message}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"서버 오류: {str(e)}"}, status=500)

    return JsonResponse({"error": "잘못된 요청입니다."}, status=400)


#아이템 목록 반환 api
@login_required
def get_items(request):
    items = Item.objects.all().values("name", "category", "price")
    return JsonResponse(list(items), safe=False)
