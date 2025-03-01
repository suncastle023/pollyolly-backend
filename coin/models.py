from django.db import models
from django.conf import settings
from django.utils import timezone
import random

class Coin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    last_rewarded_steps = models.IntegerField(default=0)
    last_reward_date = models.DateField(null=True, blank=True)
    total_feed_bonus = models.IntegerField(default=0)  # ✅ 기존 feed 보너스 저장
    total_toy_bonus = models.IntegerField(default=0)  # ✅ 기존 toy 보너스 저장

    def add_coins(self, steps):
        today = timezone.now().date()
        if self.last_reward_date != today:
            self.last_rewarded_steps = 0
            self.last_reward_date = today

        new_steps = steps - self.last_rewarded_steps
        new_steps = max(new_steps, 0)  # ✅ 음수 값 방지
        reward_count = new_steps // 50
        coins_to_add = reward_count

        # ✅ 새로 추가될 보너스를 기존 값에 누적 (새로 지급될 보너스만 추가)
        new_feed_bonus = sum(random.randint(0, 2) for _ in range(reward_count))
        new_toy_bonus = sum(random.randint(0, 3) for _ in range(reward_count))

        self.amount += coins_to_add
        self.total_feed_bonus += new_feed_bonus
        self.total_toy_bonus += new_toy_bonus
        self.last_rewarded_steps += reward_count * 50  # ✅ 마지막 보상 기준 걸음 업데이트
        self.save()

        print(f"[DEBUG] {self.user.email} | Steps: {steps} (New: {new_steps}) → Reward Count: {reward_count} → Coins Added: {coins_to_add}")
        print(f"[DEBUG] {self.user.email} | Feed Bonus: {new_feed_bonus} (Total: {self.total_feed_bonus}), Toy Bonus: {new_toy_bonus} (Total: {self.total_toy_bonus})")

        return {
            "coins": coins_to_add,
            "feed_bonus": new_feed_bonus,
            "toy_bonus": new_toy_bonus,
            "total_feed_bonus": self.total_feed_bonus,  # ✅ 누적된 보너스 값을 반환
            "total_toy_bonus": self.total_toy_bonus,    # ✅ 누적된 보너스 값을 반환
        }
