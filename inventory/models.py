from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

class Inventory(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    feed = models.IntegerField(default=5)   # 사료 개수
    toy = models.IntegerField(default=5)    # 장난감 개수
    water = models.IntegerField(default=5)  # 물 개수
    last_fed = models.DateTimeField(null=True, blank=True)   # 마지막 사료 지급 시간
    last_water = models.DateTimeField(null=True, blank=True) # 마지막 물 지급 시간

    def buy_item(self, item_type, coin):
        prices = {"feed": 3, "toy": 1, "water": 2}
        
        if item_type not in prices:
            return False, "잘못된 아이템입니다."

        if coin.amount < prices[item_type]:
            return False, "코인이 부족합니다."

        setattr(self, item_type, getattr(self, item_type) + 1)  # 아이템 증가
        coin.amount -= prices[item_type]  # 코인 차감
        self.save()
        coin.save()

        return True, f"{item_type}을(를) 구매했습니다!"
    

    def feed_pet(self, pet):
        """
        ✅ 사료를 주면 펫의 체력이 회복됩니다.
        - 사료 1개당 체력 +10 (최대 300까지)
        - 체력이 300이면 추가 회복 없음
        - 체력이 30 이상이어야 사료를 줄 수 있음
        """
        now = timezone.now()

        if pet.health < 30:
            return False, "펫의 체력이 너무 낮아 사료를 먹을 수 없습니다."
        if self.feed <= 0:
            return False, "사료가 부족합니다."

        # 체력 회복 (300 이상 증가하지 않음)
        pet.health = min(pet.health + 10, 300)

        self.feed -= 1
        self.last_fed = now
        self.save()
        pet.save()
        return True, "펫에게 사료를 줬습니다!"

    def give_water(self, pet):
        """
        ✅ 물을 주면 펫의 체력이 회복됩니다.
        - 물 1개당 체력 +30 (최대 300까지)
        - 체력이 300이면 추가 회복 없음
        - 물은 오전(00:00~11:59)와 오후(12:00~23:59) 각각 한 번만 줄 수 있음
        - 체력이 30 이상이어야 물을 줄 수 있음
        """
        now = timezone.now()
        current_hour = now.hour
        last_given = self.last_water

        if last_given:
            if last_given.date() == now.date():
                if last_given.hour < 12 and current_hour < 12:
                    return False, "오늘 오전에 이미 물을 주었습니다."
                elif last_given.hour >= 12 and current_hour >= 12:
                    return False, "오늘 오후에 이미 물을 주었습니다."

        if self.water <= 0:
            return False, "물이 부족합니다."

        # 체력 회복 (300 이상 증가하지 않음)
        pet.health = min(pet.health + 30, 300)

        self.water -= 1
        self.last_water = now
        self.save()
        pet.save()
        return True, "펫에게 물을 줬습니다!"
