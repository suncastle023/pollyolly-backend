# inventory/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Inventory
from coin.models import Coin
from pet.models import Pet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from users.models import CustomUser 

class BuyItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_name = request.data.get("item_name")
        quantity = int(request.data.get("quantity", 1))
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


class FeedPetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pet = Pet.objects.filter(owner=request.user, status="active").first()  
        inventory = Inventory.objects.get(user=request.user)
        success, message = inventory.feed_pet(pet)  # 튜플 언패킹
        if success:
            return Response({"success": True, "message": message, "health": pet.health})
        return Response({"success": False, "message": message, "health": pet.health}, status=400)
 
class GiveWaterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pet = Pet.objects.filter(owner=request.user, status="active").first()  
        inventory = Inventory.objects.get(user=request.user)
        
        success, message = inventory.give_water(pet)  # ✅ 튜플 언패킹

        # ✅ 디버깅 추가
        print(f"🔍 [DEBUG] Before Saving: last_water={inventory.last_water}")

        inventory.save()  # ✅ 저장 확실히 하기

        print(f"✅ [DEBUG] After Saving: last_water={inventory.last_water}")

        if success:
            return Response({"success": True, "message": message, "health": pet.health, "last_water": inventory.last_water})
        return Response({"success": False, "message": message, "health": pet.health, "last_water": inventory.last_water}, status=400)


class PlayWithToyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pet = Pet.objects.filter(owner=request.user, status="active").first()  
        inventory = Inventory.objects.get(user=request.user)
        toy_type = request.data.get("toy_type")  # ✅ 장난감 종류 지정
        leveled_up = False

        # ✅ 장난감 종류별 감소
        if toy_type not in ["toy1", "toy2", "toy3"]:
            return Response({"success": False, "message": "잘못된 장난감 종류입니다."}, status=400)

        if getattr(inventory, toy_type) <= 0:
            return Response({"success": False, "message": f"{toy_type}이 부족합니다."}, status=400)

        if not pet.is_active_pet():
            return Response({"success": False, "message": "현재 키우는 펫이 아닙니다."}, status=400)

        setattr(inventory, toy_type, getattr(inventory, toy_type) - 1)  # ✅ 해당 장난감 개수 감소
        inventory.save()

        leveled_up, toy_message = pet.play_with_toy(inventory, toy_type)


        response_data = {
            "success": True, 
            "message": toy_message,
            "level": pet.level,
            "experience": pet.experience,
            "status": pet.status,
            "remaining_toys": {
                "toy1": inventory.toy1,
                "toy2": inventory.toy2,
                "toy3": inventory.toy3,
            },
        }

        if leveled_up:
            response_data["message"] = f"🎉 {pet.name}의 레벨이 {pet.level}이 되었습니다! 축하합니다!"
            response_data["new_level"] = pet.level

        return Response(response_data, status=200)



class GetInventoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        inventory, _ = Inventory.objects.get_or_create(user=request.user)
        return Response(inventory.get_inventory_status())


def is_admin(user):
    """ 관리자 여부 확인 """
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)  # ✅ 관리자만 접근 가능하도록 제한
def refund_item_admin(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_email = data.get("user_email")
            item_name = data.get("item_name")

            if not user_email or not item_name:
                return JsonResponse({"error": "유저 이메일과 아이템을 입력하세요."}, status=400)

            # ✅ 이메일을 기준으로 유저 찾기
            user = get_object_or_404(CustomUser, email=user_email)
            inventory = get_object_or_404(Inventory, user=user)

            success, message = inventory.refund_item(item_name)

            if success:
                return JsonResponse({
                    "message": f"{user.nickname or user.email}의 {item_name} 환불 완료!"
                })
            return JsonResponse({"error": message}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"서버 오류: {str(e)}"}, status=500)

    return JsonResponse({"error": "잘못된 요청입니다."}, status=400)