from django.db import models
from django.conf import settings
from django.utils import timezone
import random

class Coin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)  # 게임 내 가상 코인
    last_rewarded_steps = models.IntegerField(default=0)  # 마지막으로 보상 받은 걸음 수
    last_reward_date = models.DateField(null=True, blank=True)
    total_feed_bonus = models.IntegerField(default=0)  # 총 사료 보너스
    total_toy_bonus = models.IntegerField(default=0)  # 총 장난감 보너스

    pending_coins = models.IntegerField(default=0)
    pending_feed = models.IntegerField(default=0)
    pending_toy = models.IntegerField(default=0)


    def add_coins(self, steps):
        today = timezone.now().date()
         # 오늘이 아니면 보상 기준을 리셋
        if self.last_reward_date != today:
            self.last_rewarded_steps = 0
            self.last_reward_date = today

        # 새로 추가된 걸음 수 계산 (음수가 되지 않도록 보정)
        new_steps = max(steps - self.last_rewarded_steps, 0)
        reward_count = new_steps // 50

        # 만약 reward_count가 0이면 아무 것도 지급하지 않음
        if reward_count == 0:
            return {"coins": 0, "feed_bonus": 0, "toy_bonus": 0}

        # 코인은 reward_count 만큼 지급 (즉, 각 50걸음 구간마다 1개씩)
        self.pending_coins += reward_count
        total_feed_bonus = 0
        total_toy_bonus = 0

        # reward_count만큼 각 보상마다 보너스를 랜덤으로 결정
        for _ in range(reward_count):
            total_feed_bonus += random.randint(0, 1)
            total_toy_bonus += random.randint(0, 1)

        self.pending_feed += total_feed_bonus
        self.pending_toy += total_toy_bonus

        # 지급한 보상에 해당하는 걸음 수 업데이트
        self.last_rewarded_steps += reward_count * 50
        self.save()

   
        return {"coins": self.amount, "feed_bonus": total_feed_bonus, "toy_bonus": total_toy_bonus}