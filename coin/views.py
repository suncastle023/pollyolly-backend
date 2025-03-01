from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Coin
from inventory.models import Inventory

class StepRewardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(f"[DEBUG] User: {request.user}, Authenticated: {request.user.is_authenticated}")

        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_403_FORBIDDEN)

        # 🚀 steps 값이 음수가 되지 않도록 보정
        try:
            steps = max(0, int(request.data.get("steps", 0)))  # ✅ 최소값 0 보장
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
