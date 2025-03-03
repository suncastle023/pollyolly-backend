from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Inventory
from coin.models import Coin
from pet.models import Pet

class BuyItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_type = request.data.get("item_type")
        coin = Coin.objects.get(user=request.user)
        inventory, _ = Inventory.objects.get_or_create(user=request.user)
        
        if inventory.buy_item(item_type, coin):
            return Response({"message": f"{item_type} 구매 완료!"})
        return Response({"message": "코인이 부족합니다."}, status=400)

class FeedPetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pet = Pet.objects.get(owner=request.user)
        inventory = Inventory.objects.get(user=request.user)
        success, message = inventory.feed_pet(pet)  # 튜플 언패킹
        if success:
            return Response({"success": True, "message": message, "health": pet.health})
        return Response({"success": False, "message": message, "health": pet.health}, status=400)
 
class GiveWaterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pet = Pet.objects.get(owner=request.user)
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
        pet = Pet.objects.get(owner=request.user)
        inventory = Inventory.objects.get(user=request.user)

        if pet.play_with_toy(inventory):
            return Response({
                "success": True, 
                "message": "펫과 장난감을 사용했어요!",
                "experience": pet.experience,  # ✅ 경험치 포함
                "toy": inventory.toy,  # ✅ 남은 장난감 개수 포함
            })  
        
        return Response({"success": False, "message": "장난감이 부족합니다."}, status=400)


class GetInventoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        inventory, _ = Inventory.objects.get_or_create(user=request.user)
        data = {
            "feed": inventory.feed,
            "water": inventory.water,
            "toy": inventory.toy,
        }
        return Response(data)
