from django.db import models
from django.conf import settings
import random

class Coin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    last_rewarded_steps = models.IntegerField(default=0)  # 마지막 보상 지급 시점의 누적 걸음 수

    def add_coins(self, steps):
        # 지난번 보상 지급 이후 추가된 걸음 수 계산
        new_steps = steps - self.last_rewarded_steps
        # 추가된 걸음 수가 50걸음 단위로 몇 번의 보상 대상인지 계산
        reward_count = new_steps // 50  
        coins_to_add = reward_count  # 50걸음마다 1코인 지급

        # 코인과 보너스 지급
        self.amount += coins_to_add
        # 보상이 지급된 걸음 수 만큼 업데이트
        self.last_rewarded_steps += reward_count * 50
        self.save()

        # 각 보상마다 랜덤 보너스 지급 (보상이 여러 번 발생하면 합산)
        feed_bonus = sum(random.randint(0, 2) for _ in range(reward_count))
        toy_bonus = sum(random.randint(0, 3) for _ in range(reward_count))

        print(f"[DEBUG] {self.user.email} | Steps: {steps} (New: {new_steps}) → Reward Count: {reward_count} → Coins Added: {coins_to_add}")
        print(f"[DEBUG] {self.user.email} | Feed Bonus: {feed_bonus}, Toy Bonus: {toy_bonus}")

        return {"coins": coins_to_add, "feed_bonus": feed_bonus, "toy_bonus": toy_bonus}
