from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Coin
from inventory.models import Inventory

class StepRewardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(f"[DEBUG] User: {request.user}, Authenticated: {request.user.is_authenticated}")  # 디버깅 추가
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_403_FORBIDDEN)

        # 명시적으로 정수 변환
        try:
            steps = int(request.data.get("steps", 0))
        except (ValueError, TypeError):
            steps = 0

        coin, created = Coin.objects.get_or_create(user=request.user)
        reward = coin.add_coins(steps)

        inventory, _ = Inventory.objects.get_or_create(user=request.user)
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
