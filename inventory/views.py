# inventory/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Inventory
from coin.models import Coin
from pet.models import Pet

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

        leveled_up = pet.play_with_toy(inventory)

        response_data = {
            "success": True, 
            "message": f"펫이 {toy_type}와 놀았어요!",
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
