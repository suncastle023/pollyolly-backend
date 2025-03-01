from django.db import models
from django.conf import settings
from datetime import datetime, timedelta

class Inventory(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    feed = models.IntegerField(default=5)  # 사료 개수
    toy = models.IntegerField(default=5)  # 장난감 개수
    water = models.IntegerField(default=5)  # 물 개수
    last_fed = models.DateTimeField(null=True, blank=True)  # 마지막 밥 준 시간
    last_water = models.DateTimeField(null=True, blank=True)  # 마지막 물 준 시간

    def buy_item(self, item_type, coin):
        prices = {"feed": 3, "toy": 1, "water": 2}
        if coin.amount >= prices[item_type]:
            setattr(self, item_type, getattr(self, item_type) + 1)
            coin.amount -= prices[item_type]
            self.save()
            coin.save()
            return True
        return False

    def feed_pet(self, pet):
        now = datetime.now()
        if self.feed > 0 and (not self.last_fed or now - self.last_fed > timedelta(hours=6)):
            if pet.health >= 30:
                exp_gain = 20 if pet.health >= 100 else 10  # 체력이 100 이상이면 경험치 2배
                pet.experience += exp_gain
                pet.health -= 30
                self.feed -= 1
                self.last_fed = now
                self.save()
                pet.save()
                return True
        return False

    def give_water(self, pet):
        now = datetime.now()
        current_hour = now.hour
        last_given = self.last_water

        # 오전 (00:00 ~ 11:59) / 오후 (12:00 ~ 23:59) 체크
        if last_given:
            if last_given.hour < 12 and current_hour < 12:
                return False, "오늘 오전에 이미 물을 주었습니다."
            elif last_given.hour >= 12 and current_hour >= 12:
                return False, "오늘 오후에 이미 물을 주었습니다."

        if self.water > 0 and pet.health >= 30:
            exp_gain = 60 if pet.health >= 100 else 30
            pet.experience += exp_gain
            pet.health -= 30
            self.water -= 1
            self.last_water = now
            self.save()
            pet.save()
            return True, "펫에게 물을 줬습니다!"
        
        return False, "펫의 체력이 30 이상이어야 물을 줄 수 있습니다."
