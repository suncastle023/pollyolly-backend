from django.db import models
from django.conf import settings
import random

class Coin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    def add_coins(self, steps):
        coins_to_add = steps // 50  # 50걸음마다 1코인
        self.amount += coins_to_add
        self.save()

        # 사료(2개 이하) 또는 장난감(3개 이하) 추가 지급
        feed_bonus = random.randint(0, 2)  # 0~2개 랜덤 지급
        toy_bonus = random.randint(0, 3)  # 0~3개 랜덤 지급
        
        print(f"[DEBUG] {self.user.email} | Steps: {steps} → Coins Added: {coins_to_add}")
        print(f"[DEBUG] {self.user.email} | Feed Bonus: {feed_bonus}, Toy Bonus: {toy_bonus}")

        return {"coins": coins_to_add, "feed_bonus": feed_bonus, "toy_bonus": toy_bonus}