from django.urls import path
from .views import StepRewardAPIView

app_name = 'coin'

urlpatterns = [
    path("reward/", StepRewardAPIView.as_view(), name="step_reward"),
]
