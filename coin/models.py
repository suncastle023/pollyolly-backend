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

    def add_coins(self, steps):
        today = timezone.now().date()
        # 만약 마지막 보상 지급 날짜가 오늘이 아니라면 보상 기준을 리셋
        if self.last_reward_date != today:
            self.last_rewarded_steps = 0
            self.last_reward_date = today

        # 새로 추가된 걸음 수 계산 (음수가 되지 않도록 보정)
        new_steps = max(steps - self.last_rewarded_steps, 0)
        reward_count = new_steps // 50
        coins_to_add = reward_count

        # 만약 reward_count가 0이면 아무 것도 지급하지 않음
        if reward_count == 0:
            return {"coins": 0, "feed_bonus": 0, "toy_bonus": 0}

        # 보너스는 새로 지급되는 횟수만큼 계산
        new_feed_bonus = sum(random.randint(0, 2) for _ in range(reward_count))
        new_toy_bonus = sum(random.randint(0, 3) for _ in range(reward_count))

        self.amount += coins_to_add
        self.last_rewarded_steps += reward_count * 50
        self.save()

        print(f"[DEBUG] {self.user.email} | Steps: {steps} (New: {new_steps}) → Reward Count: {reward_count} → Coins Added: {coins_to_add}")
        print(f"[DEBUG] {self.user.email} | New Feed Bonus: {new_feed_bonus}, New Toy Bonus: {new_toy_bonus}")

        return {"coins": coins_to_add, "feed_bonus": new_feed_bonus, "toy_bonus": new_toy_bonus}
