from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Coin

class StepRewardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        steps = request.data.get("steps", 0)
        coin, created = Coin.objects.get_or_create(user=request.user)
        reward = coin.add_coins(steps)
        return Response(reward)
