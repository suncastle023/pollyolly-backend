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

    # 각 pending 코인에 대해 개별 랜덤 보상 결과를 저장하는 필드
    # 각 항목은 {"feed": 0 또는 1, "toy": 0 또는 1} 형식입니다.
    pending_rewards = models.JSONField(default=list, blank=True)

    @property
    def pending_coins(self):
        return len(self.pending_rewards)

    @property
    def pending_feed(self):
        return sum(reward.get("feed", 0) for reward in self.pending_rewards)

    @property
    def pending_toy(self):
        return sum(reward.get("toy", 0) for reward in self.pending_rewards)

    def add_coins(self, steps):
        today = timezone.now().date()
        if self.last_reward_date != today:
            self.last_rewarded_steps = 0
            self.last_reward_date = today
            self.pending_rewards = []  # 새로운 날이면 기존 pending 보상 초기화

        new_steps = max(steps - self.last_rewarded_steps, 0)
        reward_count = new_steps // 50

        if reward_count == 0:
            return {"coins": self.amount, "feed_bonus": 0, "toy_bonus": 0}

        # 각 50걸음 구간마다 개별 랜덤 보상(0 또는 1)을 결정해서 pending_rewards에 추가
        for _ in range(reward_count):
            reward = {"feed": random.randint(0, 1), "toy": random.randint(0, 1)}
            self.pending_rewards.append(reward)

        self.last_rewarded_steps += reward_count * 50
        self.save()

        total_feed = self.pending_feed
        total_toy = self.pending_toy

        return {"coins": self.amount, "feed_bonus": total_feed, "toy_bonus": total_toy}
    
def reset_daily_steps(self):
    today = timezone.now().date()
    if self.last_reward_date != today:
        self.last_rewarded_steps = 0
        self.last_reward_date = today
        self.save()
