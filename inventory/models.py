from django.db import models
from django.conf import settings
from store.models import Item
from django.utils import timezone

class Inventory(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # 일반 & 프리미엄 아이템 개수
    feed = models.IntegerField(default=5)   # 일반 사료
    pm_feed = models.IntegerField(default=0)  # 프리미엄 사료
    toy1 = models.IntegerField(default=5)  # 장난감1
    toy2 = models.IntegerField(default=0)  # 장난감2
    toy3 = models.IntegerField(default=0)  # 장난감3
    water = models.IntegerField(default=5)  # 일반 물
    pm_water = models.IntegerField(default=0)  # 프리미엄 물

    # 배경 & 집 아이템
    backgrounds = models.ManyToManyField(Item, related_name="user_backgrounds", blank=True)
    houses = models.ManyToManyField(Item, related_name="user_houses", blank=True)

    # 마지막 지급 시간
    last_fed = models.DateTimeField(null=True, blank=True)
    last_water = models.DateTimeField(null=True, blank=True)

    def buy_item(self, item_name, coin, quantity=1):
        """
        ✅ 아이템 구매 로직
        - 일반 & 프리미엄 사료/물/장난감 개수 증가
        - 배경 & 집 아이템도 개수 증가
        """
        item = Item.objects.filter(name=item_name).first()
        if not item:
            return False, "잘못된 아이템입니다."

        total_price = item.price * quantity
        if coin.amount < total_price:
            return False, f"코인이 부족합니다. 최대 {coin.amount // item.price}개까지 구매 가능합니다."

        # 카테고리별 처리
        if item.name in ["feed", "pm_feed"]:
            setattr(self, item.name, getattr(self, item.name, 0) + quantity)
        elif item.name in ["toy1", "toy2", "toy3"]:
            setattr(self, item.name, getattr(self, item.name, 0) + quantity)
        elif item.name in ["water", "pm_water"]:
            setattr(self, item.name, getattr(self, item.name, 0) + quantity)
        elif item.category == "background":
            # ✅ 배경 중복 구매 시 개수 증가
            if self.backgrounds.filter(name=item.name).exists():
                pass  # 이미 존재하면 개수만 증가 (ManyToManyField 자체는 중복 불가)
            else:
                self.backgrounds.add(item)  # 없으면 추가
        elif item.category == "house":
            if item.name == "cat_tower" and not self.user.has_cat():
                return False, "캣타워는 고양이 전용입니다."
            # ✅ 집 중복 구매 시 개수 증가
            if self.houses.filter(name=item.name).exists():
                pass
            else:
                self.houses.add(item)

        # 코인 차감 및 저장
        coin.amount -= total_price
        coin.save()
        self.save()
        return True, f"{item.name}을(를) {quantity}개 구매했습니다!"


    def get_inventory_status(self):
        """
        ✅ 인벤토리 상태 반환 (일반 아이템 + 배경/집 아이템 개수 포함)
        """
        # 일반 아이템 개수
        inventory_data = {
            "feed": self.feed,
            "pm_feed": self.pm_feed,
            "toy1": self.toy1,
            "toy2": self.toy2,
            "toy3": self.toy3,
            "water": self.water,
            "pm_water": self.pm_water,
        }

        # 배경 & 집 아이템 개수 추가
        background_items = self.backgrounds.values("name").annotate(count=models.Count("name"))
        house_items = self.houses.values("name").annotate(count=models.Count("name"))

        inventory_data["backgrounds"] = {item["name"]: item["count"] for item in background_items}
        inventory_data["houses"] = {item["name"]: item["count"] for item in house_items}

        return inventory_data


    def feed_pet(self, pet):
        """
        사료를 주면 펫의 체력이 회복됩니다.
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
        물을 주면 펫의 체력이 회복됩니다.
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
