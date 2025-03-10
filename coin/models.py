from django.db import models
from django.conf import settings
from django.utils import timezone
import random

class Coin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)  
    last_rewarded_steps = models.IntegerField(default=0)  
    last_reward_date = models.DateField(null=True, blank=True)
    total_feed_bonus = models.IntegerField(default=0)  
    total_toy1_bonus = models.IntegerField(default=0) 

    pending_coins = models.IntegerField(default=0)
    pending_feed = models.IntegerField(default=0)
    pending_toy1 = models.IntegerField(default=0)  

    pending_rewards = models.JSONField(default=list)  
    #  [{"feed": 1, "toy1": 0}, {"feed": 0, "toy1": 1}]

    def add_coins(self, steps):
        today = timezone.now().date()

        if self.last_reward_date != today:
            self.last_rewarded_steps = 0
            self.last_reward_date = today

        new_steps = max(steps - self.last_rewarded_steps, 0)
        reward_count = new_steps // 50

        if reward_count == 0:
            return {"coins": 0, "feed_bonus": 0, "toy1_bonus": 0}

        self.pending_coins += reward_count
        total_feed_bonus = 0
        total_toy1_bonus = 0

        rewards = []
        for _ in range(reward_count):
            feed_bonus = random.randint(0, 1)
            toy1_bonus = random.randint(0, 1) 
            rewards.append({"feed": feed_bonus, "toy1": toy1_bonus})

            total_feed_bonus += feed_bonus
            total_toy1_bonus += toy1_bonus

        self.pending_feed += total_feed_bonus
        self.pending_toy1 += total_toy1_bonus 
        self.pending_rewards.extend(rewards) 

        self.last_rewarded_steps += reward_count * 50
        self.save()

        return {
            "coins": self.amount, 
            "feed_bonus": total_feed_bonus, 
            "toy1_bonus": total_toy1_bonus,  
        }
    
    def reset_daily_steps(self):
        """ ✅ 새로운 날이 되면 보상 받은 걸음 수 초기화 """
        today = timezone.now().date()
        if self.last_reward_date != today:
            self.last_rewarded_steps = 0
            self.last_reward_date = today
            self.save()
