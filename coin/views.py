from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Coin
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import status


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
        today = timezone.now().date()
        # 오늘이 아니면 보상 기준 리셋
        if coin.last_reward_date != today:
            coin.last_rewarded_steps = 0
            coin.last_reward_date = today

        # 기존 add_coins 로직을 호출하여 보상 계산 (이미 coin.amount에 더해짐)
        reward = coin.add_coins(steps)
        # 지급되지 않은 보상은 reward["coins"] (즉, 이번 호출 후 총 코인 수)
        # 대신 pending_coins에 보상 값을 그대로 넣음
        coin.pending_coins = reward["coins"]
        # 보너스도 pending에 저장 (필요에 따라 추가 조정 가능)
        coin.pending_feed = reward["feed_bonus"]
        coin.pending_toy = reward["toy_bonus"]
        coin.save()

        return Response({
            "pending_coins": coin.pending_coins,
            "pending_feed": coin.pending_feed,
            "pending_toy": coin.pending_toy,
            "message": "Pending rewards are updated. Press the coin button to claim rewards."
        })
    

class ClaimCoinAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_403_FORBIDDEN)

        coin, _ = Coin.objects.get_or_create(user=request.user)

        if coin.pending_coins > 0:
            # 한 번 누를 때마다 1코인씩 지급 (최대 100개 제한)
            coin.amount = min(100, coin.amount + 1)
            coin.pending_coins -= 1

            # 각 코인 지급에 대해, pending_feed와 pending_toy가 있다면 1씩 지급하고 차감
            feed_bonus = 1 if coin.pending_feed > 0 else 0
            toy_bonus = 1 if coin.pending_toy > 0 else 0

            if feed_bonus:
                coin.pending_feed -= 1
            if toy_bonus:
                coin.pending_toy -= 1

            from inventory.models import Inventory
            inventory, _ = Inventory.objects.get_or_create(user=request.user)
            inventory.feed += feed_bonus
            inventory.toy += toy_bonus
            inventory.save()

            coin.save()

            return Response({
                "message": "1 reward claimed successfully",
                "claimed_coin": 1,
                "claimed_feed": feed_bonus,
                "claimed_toy": toy_bonus,
                "total_coins": coin.amount,
                "pending_coins": coin.pending_coins,
                "pending_feed": coin.pending_feed,
                "pending_toy": coin.pending_toy,
                "total_feed": inventory.feed,
                "total_toy": inventory.toy,
            })
        else:
            return Response({"message": "No rewards to claim"}, status=status.HTTP_400_BAD_REQUEST)



#유저의 현재 코인 잔액을 반환하는 API
@login_required
def get_user_coins(request):
    coin = get_object_or_404(Coin, user=request.user)
    return JsonResponse({"coins": coin.amount})