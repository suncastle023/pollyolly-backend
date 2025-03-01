from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

class Inventory(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    feed = models.IntegerField(default=5)  # 사료 개수
    toy = models.IntegerField(default=5)  # 장난감 개수
    water = models.IntegerField(default=5)  # 물 개수
    last_fed = models.DateTimeField(null=True, blank=True)  # 마지막 밥 준 시간
    last_water = models.DateTimeField(null=True, blank=True)  # 마지막 물 준 시간

    def buy_item(self, item_type, coin):
        """아이템을 구매하는 함수"""
        prices = {"feed": 3, "toy": 1, "water": 2}
        if coin.amount >= prices[item_type]:
            setattr(self, item_type, getattr(self, item_type) + 1)
            coin.amount -= prices[item_type]
            self.save()
            coin.save()
            return True
        return False

    def feed_pet(self, pet):
        """사료를 주는 함수 - 제한 없이 언제든지 줄 수 있음"""
        now = timezone.now()

        # ✅ 디버깅 로그 추가
        print(f"[DEBUG] feed_pet() called → feed={self.feed}, last_fed={self.last_fed}, now={now}, pet_exp={pet.experience}")

        if self.feed <= 0:
            print("[DEBUG] ❌ 사료가 부족합니다.")
            return False, "사료가 부족합니다."

        if pet.experience < 30:
            print("[DEBUG] ❌ 펫의 경험치가 부족합니다.")
            return False, "펫의 경험치가 30 이상이어야 합니다."

        exp_gain = 20 if pet.experience >= 100 else 10  # ✅ 경험치 보상
        pet.experience = min(pet.experience + exp_gain, 100)  # ✅ 최대 경험치 100 제한
        self.feed -= 1
        self.last_fed = now  # ✅ 마지막 먹이 준 시간 업데이트
        self.save()
        pet.save()

        return True, "펫에게 사료를 줬습니다!"

    def give_water(self, pet):
        """물을 주는 함수 - 오전과 오후 각각 1번만 가능"""
        now = timezone.now()
        current_hour = now.hour
        last_given = self.last_water

        # ✅ 디버깅 로그 추가
        print(f"[DEBUG] give_water() called → water={self.water}, last_water={self.last_water}, now={now}, pet_exp={pet.experience}")

        if last_given:
            last_given_hour = last_given.hour

            if last_given_hour < 12 and current_hour < 12:
                print("[DEBUG] ❌ 오늘 오전에 이미 물을 줬습니다.")
                return False, "오늘 오전에 이미 물을 주었습니다."
            elif last_given_hour >= 12 and current_hour >= 12:
                print("[DEBUG] ❌ 오늘 오후에 이미 물을 줬습니다.")
                return False, "오늘 오후에 이미 물을 주었습니다."

        if self.water <= 0:
            print("[DEBUG] ❌ 물이 부족합니다.")
            return False, "물이 부족합니다."

        if pet.experience < 30:
            print("[DEBUG] ❌ 펫의 경험치가 부족합니다.")
            return False, "펫의 경험치가 30 이상이어야 물을 줄 수 있습니다."

        exp_gain = 60 if pet.experience >= 100 else 30
        pet.experience = min(pet.experience + exp_gain, 100)  # ✅ 최대 경험치 100 제한
        self.water -= 1
        self.last_water = now  # ✅ 마지막 물 준 시간 업데이트
        self.save()
        pet.save()

        return True, "펫에게 물을 줬습니다!"
