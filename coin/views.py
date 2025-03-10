from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Coin
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import status
from inventory.models import Inventory
import logging

logger = logging.getLogger(__name__)

class StepRewardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        coin, _ = Coin.objects.get_or_create(user=request.user)
        return Response({
            "coins": coin.amount,  
            "pending_coins": coin.pending_coins,
            "pending_feed": coin.pending_feed,
            "pending_toy1": coin.pending_toy1,  
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


        coin.add_coins(steps)
        coin.save()

        return Response({
            "coins": coin.amount,
            "pending_coins": coin.pending_coins,
            "pending_feed": coin.pending_feed,
            "pending_toy1": coin.pending_toy1,
            "message": "Pending rewards are updated. Press the coin button to claim rewards."
        })


class ClaimCoinAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_403_FORBIDDEN)

        coin, _ = Coin.objects.get_or_create(user=request.user)

        if not isinstance(coin.pending_rewards, list):
            coin.pending_rewards = []


        if len(coin.pending_rewards) != coin.pending_coins:
            logger.warning(f"⚠️ {coin.user}의 보류 코인({coin.pending_coins})과 보류 보상({len(coin.pending_rewards)}) 불일치 감지")
            
            if len(coin.pending_rewards) < coin.pending_coins:
                missing_rewards = [{"feed": 0, "toy1": 0} for _ in range(coin.pending_coins - len(coin.pending_rewards))]
                coin.pending_rewards.extend(missing_rewards)
            else:
                coin.pending_rewards = coin.pending_rewards[:coin.pending_coins]

            coin.save()

        if coin.pending_coins > 0 and coin.pending_rewards:
            reward = coin.pending_rewards.pop(0) 

            coin.amount += 1  
            coin.pending_coins -= 1

            feed_bonus = reward.get("feed", 0)
            toy1_bonus = reward.get("toy1", 0) 

            if coin.pending_feed >= feed_bonus:
                coin.pending_feed -= feed_bonus
            else:
                feed_bonus = 0 

            if coin.pending_toy1 >= toy1_bonus:
                coin.pending_toy1 -= toy1_bonus
            else:
                toy_bonus = 0  


            inventory, _ = Inventory.objects.get_or_create(user=request.user)
            inventory.feed += feed_bonus
            inventory.toy1 += toy_bonus 
            inventory.save()

            coin.save()

            return Response({
                "message": "1 reward claimed successfully",
                "claimed_coin": 1,
                "claimed_feed": feed_bonus,
                "claimed_toy1": toy_bonus, 
                "total_coins": coin.amount,
                "pending_coins": coin.pending_coins,
                "pending_feed": coin.pending_feed,
                "pending_toy1": coin.pending_toy1, 
                "total_feed": inventory.feed,
                "total_toy1": inventory.toy1,  
            })
        else:
            return Response({"message": "No rewards to claim"}, status=status.HTTP_400_BAD_REQUEST)


# ✅ 유저의 현재 코인 잔액을 반환하는 API
@login_required
def get_user_coins(request):
    coin = get_object_or_404(Coin, user=request.user)
    return JsonResponse({
        "coins": coin.amount,
        "pending_coins": coin.pending_coins,
        "pending_feed": coin.pending_feed,
        "pending_toy1": coin.pending_toy1, 
    })
