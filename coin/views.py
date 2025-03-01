from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Coin
from inventory.models import Inventory

class StepRewardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        steps = request.data.get("steps", 0)
        coin, created = Coin.objects.get_or_create(user=request.user)
        reward = coin.add_coins(steps)

        # 사용자 인벤토리 가져오기 (없으면 생성)
        inventory, _ = Inventory.objects.get_or_create(user=request.user)
        
        # 지급된 보상을 인벤토리에 반영
        inventory.feed += reward["feed_bonus"]
        inventory.toy += reward["toy_bonus"]
        inventory.save()

        return Response({
            "rewarded_coins": reward["coins"],
            "total_coins": coin.amount,
            "feed_bonus": reward["feed_bonus"],
            "toy_bonus": reward["toy_bonus"],
            "updated_feed": inventory.feed,
            "updated_toy": inventory.toy,
        })
