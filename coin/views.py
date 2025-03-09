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

    def get(self, request):
        coin, _ = Coin.objects.get_or_create(user=request.user)
        return Response({
            "coins": coin.amount,  
            "pending_coins": coin.pending_coins,
            "pending_feed": coin.pending_feed,
            "pending_toy": coin.pending_toy,
    
        })
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_403_FORBIDDEN)

        try:
            steps = max(0, int(request.data.get("steps", 0)))
        except (ValueError, TypeError):
            steps = 0

        coin, created = Coin.objects.get_or_create(user=request.user)
        today = timezone.now().date()
        if coin.last_reward_date != today:
            coin.last_rewarded_steps = 0
            coin.last_reward_date = today

        # add_coins 내부에서 pending 코인이 올바르게 누적되고 저장됨
        coin.add_coins(steps)
        coin.save()

        return Response({
            "coins": coin.amount,
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
            # pending_rewards 리스트에서 첫 번째 항목을 꺼내서 그 보상을 지급
            reward = coin.pending_rewards.pop(0)
            coin.amount += 1  # 코인 1 지급

            feed_bonus = reward.get("feed", 0)
            toy_bonus = reward.get("toy", 0)

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