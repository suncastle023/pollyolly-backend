from django.db import models
from django.conf import settings
import random

class Coin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    last_rewarded_steps = models.IntegerField(default=0)  # 마지막 보상 지급 시점의 누적 걸음 수

    def add_coins(self, steps):
        # 만약 마지막 보상 기준을 저장하는 필드가 없다면 추가하는 것이 좋습니다.
        # 예를 들어, self.last_rewarded_steps를 생성하고, 처음에는 0으로 초기화했다고 가정합니다.
        # 만약 없다면 아래 코드는 단순히 steps // 50을 사용하게 됩니다.
        # reward_count: 마지막 보상 이후 추가된 50걸음의 횟수
        new_steps = steps - getattr(self, 'last_rewarded_steps', 0)
        reward_count = new_steps // 50
        
        coins_to_add = reward_count  # 50걸음마다 1코인 지급

        # 보상이 지급되었다면, bonus도 reward_count 횟수만큼 지급
        feed_bonus = 0
        toy_bonus = 0
        if reward_count > 0:
            feed_bonus = sum(random.randint(0, 2) for _ in range(reward_count))
            toy_bonus = sum(random.randint(0, 3) for _ in range(reward_count))
            # 보상 지급 후, 마지막 보상 기준 갱신 (예: 기존 값에 지급된 50걸음만큼 추가)
            if hasattr(self, 'last_rewarded_steps'):
                self.last_rewarded_steps += reward_count * 50
            else:
                self.last_rewarded_steps = reward_count * 50

        self.amount += coins_to_add
        self.save()

        print(f"[DEBUG] {self.user.email} | Steps: {steps} (New: {new_steps}) → Reward Count: {reward_count} → Coins Added: {coins_to_add}")
        print(f"[DEBUG] {self.user.email} | Feed Bonus: {feed_bonus}, Toy Bonus: {toy_bonus}")

        return {"coins": coins_to_add, "feed_bonus": feed_bonus, "toy_bonus": toy_bonus}
