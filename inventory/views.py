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
        pet = Pet.objects.get(user=request.user)
        inventory = Inventory.objects.get(user=request.user)
        if inventory.feed_pet(pet):
            return Response({"message": "펫에게 밥을 줬어요!"})
        return Response({"message": "밥을 줄 수 없는 상태입니다."}, status=400)

class GiveWaterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pet = Pet.objects.get(user=request.user)
        inventory = Inventory.objects.get(user=request.user)
        success, message = inventory.give_water(pet)
        
        if success:
            return Response({"message": message})
        return Response({"message": message}, status=400)

class PlayWithToyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pet = Pet.objects.get(user=request.user)
        inventory = Inventory.objects.get(user=request.user)
        if pet.play_with_toy(inventory):
            return Response({"message": "펫과 장난감을 사용했어요!"})
        return Response({"message": "장난감이 부족합니다."}, status=400)
