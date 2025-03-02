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
            return Response({"success": True, "message": message})  # ✅ success 추가
        return Response({"success": False, "message": message}, status=400)  # ✅ 실패 응답에도 추가

 
class GiveWaterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pet = Pet.objects.get(owner=request.user)
        inventory = Inventory.objects.get(user=request.user)
        success, message = inventory.give_water(pet)  # 튜플 언패킹
        if success:
            return Response({"success": True, "message": message})  # ✅ success 추가
        return Response({"success": False, "message": message}, status=400)  # ✅ 실패 응답에도 추가



class PlayWithToyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pet = Pet.objects.get(owner=request.user)
        inventory = Inventory.objects.get(user=request.user)
        if pet.play_with_toy(inventory):
            return Response({"success": True, "message": "펫과 장난감을 사용했어요!"})  # ✅ success 추가
        return Response({"success": False, "message": "장난감이 부족합니다."}, status=400)  # ✅ 실패 응답에도 추가


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
