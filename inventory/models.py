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
        if coin.amount >= prices[item_type]:
            setattr(self, item_type, getattr(self, item_type) + 1)
            coin.amount -= prices[item_type]
            self.save()
            coin.save()
            return True
        return False

    def feed_pet(self, pet):
        """
        사료를 주면 pet의 경험치(체력)를 회복시킵니다.
        - 사료 한 개당 +10 exp, 단, pet.experience가 100 이상이면 2배 (+20)
        - 사료는 언제든지 줄 수 있습니다.
        - 단, 펫의 경험치가 30 미만이면 사료를 줄 수 없습니다.
        """
        now = timezone.now()

        if pet.experience < 30:
            return False, "펫의 체력이 너무 낮아 사료를 먹을 수 없습니다."
        if self.feed <= 0:
            return False, "사료가 부족합니다."

        # 경험치 회복량 결정
        exp_gain = 20 if pet.experience >= 100 else 10
        pet.experience = min(pet.experience + exp_gain, 100)

        self.feed -= 1
        self.last_fed = now
        self.save()
        pet.save()
        return True, "펫에게 사료를 줬습니다!"

    def give_water(self, pet):
        """
        물을 주면 pet의 경험치(체력)를 회복시킵니다.
        - 물 한 개당 +30 exp, 단, pet.experience가 100 이상이면 2배 (+60)
        - 물은 오전(00:00~11:59)와 오후(12:00~23:59) 각각 한 번만 줄 수 있습니다.
        - 단, 펫의 경험치가 30 미만이면 물을 줄 수 없습니다.
        """
        now = timezone.now()
        current_hour = now.hour
        last_given = self.last_water

        if last_given:
            # ✅ 날짜가 다르면 리셋
            if last_given.date() == now.date():
                # ✅ 같은 날짜일 때만 오전/오후 제한 적용
                # 오전/오후 한정: 동일 구간에 이미 물을 준 경우
                if last_given:
                    if last_given.hour < 12 and current_hour < 12:
                        return False, "오늘 오전에 이미 물을 주었습니다."
                    elif last_given.hour >= 12 and current_hour >= 12:
                        return False, "오늘 오후에 이미 물을 주었습니다."
     
     
        if self.water <= 0:
            return False, "물이 부족합니다."

        exp_gain = 60 if pet.experience >= 100 else 30
        pet.experience = min(pet.experience + exp_gain, 100)

        self.water -= 1
        self.last_water = now
        self.save()
        pet.save()
        return True, "펫에게 물을 줬습니다!"
