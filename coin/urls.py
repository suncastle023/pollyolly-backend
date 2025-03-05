from django.urls import path
from .views import StepRewardAPIView, get_user_coins

app_name = 'coin'

urlpatterns = [
    path("reward/", StepRewardAPIView.as_view(), name="step_reward"),
    path("IhaveCoin/", get_user_coins, name="amount_of_coin"),


]
