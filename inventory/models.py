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

     # 새로 구매한 아이템을 저장하는 JSONField
    purchased_items = models.JSONField(default=dict, blank=True)  

    # 마지막 지급 시간
    last_fed = models.DateTimeField(null=True, blank=True)
    last_water = models.DateTimeField(null=True, blank=True)

    def buy_item(self, item_name, coin, quantity=1):
        """
        아이템 구매 로직
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

        # 구매한 아이템 JSONField에 저장
        purchased_items = self.purchased_items
        if item.name in purchased_items:
            purchased_items[item.name] += quantity
        else:
            purchased_items[item.name] = quantity
        
        self.purchased_items = purchased_items


        # 코인 차감 및 저장
        coin.amount -= total_price
        coin.save()
        self.save()
        return True, f"{item.name}을(를) {quantity}개 구매했습니다!"

    #환불 로직
    def refund_item(self, item_name):
        from coin.models import Coin 

        if item_name not in self.purchased_items:
            return False, "환불할 아이템이 없습니다."

        item = Item.objects.filter(name=item_name).first()
        if not item:
            return False, "잘못된 아이템입니다."

        coin = Coin.objects.get(user=self.user)
        refund_amount = item.price * self.purchased_items[item_name]
        coin.amount += refund_amount
        coin.save()

        del self.purchased_items[item_name]
        self.save()

        return True, f"{item_name}을(를) 환불하였습니다."

    #인벤토리 상태 반환
    def get_inventory_status(self):
        # 일반 아이템 개수
        inventory_data = {
            "feed": self.feed,
            "pm_feed": self.pm_feed,
            "toy1": self.toy1,
            "toy2": self.toy2,
            "toy3": self.toy3,
            "water": self.water,
            "pm_water": self.pm_water,
            "purchased_items": self.purchased_items,
        }

        # 배경 & 집 아이템 개수 추가
        background_items = self.backgrounds.values("name").annotate(count=models.Count("name"))
        house_items = self.houses.values("name").annotate(count=models.Count("name"))

        inventory_data["backgrounds"] = {item["name"]: item["count"] for item in background_items}
        inventory_data["houses"] = {item["name"]: item["count"] for item in house_items}

        return inventory_data
    def __str__(self):
        return f"{self.user.username}의 인벤토리"


    def feed_pet(self, pet, feed_type="feed"):
        """
        사료를 주면 펫의 체력이 회복됩니다.
        - 일반 사료(feed): 체력 +10, 경험치 +0
        - 프리미엄 사료(pm_feed): 체력 +30, 경험치 +5
        - 체력이 30 미만이면 먹을 수 없음
        """
        now = timezone.now()

        if pet.health < 30:
            return False, "펫의 체력이 너무 낮아 사료를 먹을 수 없습니다."
        if feed_type not in ["feed", "pm_feed"]:
            return False, "잘못된 사료 유형입니다."
        if getattr(self, feed_type) <= 0:
            return False, f"{feed_type}이 부족합니다."

        # 경험치 증가 없음 (일반 사료) / 경험치 증가 (프리미엄 사료)
        health_gain = 10 if feed_type == "feed" else 30
        exp_gain = 0 if feed_type == "feed" else 5  # ✅ 일반 사료 경험치 0, 프리미엄 사료 경험치 5

        pet.health = min(pet.health + health_gain, 300)
        pet.experience += exp_gain  

        setattr(self, feed_type, getattr(self, feed_type) - 1)  # 사료 개수 감소
        self.last_fed = now
        self.save()
        pet.save()

        return True, f"{feed_type}을(를) 먹였습니다! (+{health_gain} 체력, +{exp_gain} 경험치)"


    def give_water(self, pet, water_type="water"):
        """
        물을 주면 펫의 체력이 회복됩니다.
        - 일반 물(water): 체력 +30, 경험치 +0
        - 프리미엄 물(pm_water): 체력 +60, 경험치 +10
        - 오전/오후 각각 한 번만 줄 수 있음
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

        if water_type not in ["water", "pm_water"]:
            return False, "잘못된 물 유형입니다."
        if getattr(self, water_type) <= 0:
            return False, f"{water_type}이 부족합니다."

        # 경험치 증가 없음 (일반 물) / 경험치 증가 (프리미엄 물)
        health_gain = 30 if water_type == "water" else 60
        exp_gain = 0 if water_type == "water" else 10  # ✅ 일반 물 경험치 0, 프리미엄 물 경험치 10

        pet.health = min(pet.health + health_gain, 300)
        pet.experience += exp_gain  

        setattr(self, water_type, getattr(self, water_type) - 1)  # 물 개수 감소
        self.last_water = now
        self.save()
        pet.save()

        return True, f"{water_type}을(를) 마셨습니다! (+{health_gain} 체력, +{exp_gain} 경험치)"
