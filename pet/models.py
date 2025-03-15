from django.db import models
from django.conf import settings
import random
from datetime import timedelta
from django.utils import timezone

class Pet(models.Model):
    STATUS_CHOICES = [
        ("active", "현재 키우는 중"),
        ("neglected", "관리를 안 해서 죽음"),
        ("aged", "늙어서 자연사"),
    ]

    PET_TYPES = {
        "dog": ["blackDog", "whiteDog", "yellowDog"],
        "cat": ["Cat"],
    }

    LEVEL_UNLOCKS = [
        (1, ["dog", "cat"]),
    ]



    IMAGE_PATHS = {
        "whiteDog": "assets/pet_images/whiteDog.png",
        "whiteDogR": "assets/pet_images/whiteDogR.png",
        "whiteDogR": "assets/pet_images/whiteDogL.png",
        "dtywhiteDog": "assets/pet_images/dtywhiteDog.png",
        "dtywhiteDog": "assets/pet_images/dtywhiteDogR.png",
        "dtywhiteDog": "assets/pet_images/dtywhiteDogL.png",

        "yellowDog": "assets/pet_images/yellowDog.png",
        "yellowDogL": "assets/pet_images/yellowDogL.png",
        "yellowDogR": "assets/pet_images/yellowDogR.png",

        "blackDog": "assets/pet_images/blackDog.png",
        "blackDogL": "assets/pet_images/blackDogL.png",
        "blackDogR": "assets/pet_images/blackDogR.png",

        "Cat": "assets/pet_images/Cat.png",
        "CatL": "assets/pet_images/CatL.png",
        "CatR": "assets/pet_images/CatR.png",

    }


    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=20)
    breed = models.CharField(max_length=20)
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0) 
    health = models.IntegerField(default=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")  
    last_activity = models.DateTimeField(default=timezone.now) 
    image_path = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        """자동으로 이미지 경로 설정"""
        if self.breed in self.PET_TYPES.get(self.pet_type, []):
            self.image_path = f"assets/pet_images/{self.breed}.png"
        """펫 상태 자동 업데이트"""
        if self.health <= 0:
            self.status = "neglected"
            self.owner.level = max(1, self.owner.level - 1)  # ✅ 사용자의 레벨 1 감소
            self.owner.save()
        elif self.level >= 10 and self.experience >= 100:
            self.status = "aged"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.breed}) - Lv.{self.level} ({self.status})"

    def is_active_pet(self):
        """ ✅ 현재 키우는 펫인지 확인 """
        return self.status == "active"

    def set_pet_status(self, new_status):
        """ ✅ 펫 상태 변경 함수 """
        if new_status in dict(self.STATUS_CHOICES):
            if new_status == "neglected":
                self.decrease_owner_level() 
            self.status = new_status
            self.save()

    def decrease_owner_level(self):
        """ ✅ 사용자의 레벨이 1 이상이면 1 감소 """
        if hasattr(self.owner, "level") and self.owner.level > 1:
            self.owner.level -= 1
            self.owner.save()

    @classmethod
    def get_available_pets(cls, level):
        available_pets = []
        for lvl, pets in cls.LEVEL_UNLOCKS:
            if level >= lvl:
                available_pets.extend(pets)
        return available_pets

    @classmethod
    def get_random_pet(cls, level):
        available_pets = cls.get_available_pets(level)
        if not available_pets:
            return None, None

        chosen_type = random.choice(available_pets)
        chosen_breed = random.choice(cls.PET_TYPES[chosen_type])
        return chosen_type, chosen_breed


    def feed_pet(self, inventory, feed_type="feed"):
        """ ✅ 사료를 주면 체력 회복 및 경험치 증가 """
        if feed_type not in ["feed", "pm_feed"]:
            return False, "잘못된 사료 유형입니다."
        if getattr(inventory, feed_type) <= 0:
            return False, f"{feed_type}이 부족합니다."
        if self.health < 30:
            return False, "펫의 체력이 너무 낮아 사료를 먹을 수 없습니다."

        health_gain = 10 if feed_type == "feed" else 30
        exp_gain = 0 if feed_type == "feed" else 5  # ✅ 일반 사료 경험치 0, 프리미엄 사료 경험치 5

        self.health = min(self.health + health_gain, 300)
        setattr(inventory, feed_type, getattr(inventory, feed_type) - 1)  # ✅ 사료 개수 감소
        inventory.save()
        self.gain_experience(exp_gain)  # ✅ 경험치 증가 반영
        return True, f"{feed_type}을(를) 먹였습니다! (+{health_gain} 체력, +{exp_gain} 경험치)"


    def give_water(self, inventory, water_type="water"):
        """ ✅ 물을 주면 체력 회복 및 경험치 증가 """
        if water_type not in ["water", "pm_water"]:
            return False, "잘못된 물 유형입니다."
        if getattr(inventory, water_type) <= 0:
            return False, f"{water_type}이 부족합니다."

        now = timezone.now()
        last_given = inventory.last_water

        if last_given:
            if last_given.date() == now.date():
                if last_given.hour < 12 and now.hour < 12:
                    return False, "오늘 오전에 이미 물을 주었습니다."
                elif last_given.hour >= 12 and now.hour >= 12:
                    return False, "오늘 오후에 이미 물을 주었습니다."

        health_gain = 30 if water_type == "water" else 60
        exp_gain = 0 if water_type == "water" else 10  # ✅ 일반 물 경험치 0, 프리미엄 물 경험치 10

        self.health = min(self.health + health_gain, 300)
        setattr(inventory, water_type, getattr(inventory, water_type) - 1)  # ✅ 물 개수 감소
        inventory.last_water = now
        inventory.save()
        self.gain_experience(exp_gain)  # ✅ 경험치 증가 반영
        return True, f"{water_type}을(를) 마셨습니다! (+{health_gain} 체력, +{exp_gain} 경험치)"



    def gain_experience(self, exp_gain):
        """ ✅ 경험치 증가 및 자동 레벨업 """
        if not self.is_active_pet():
            return False  # ✅ 과거 펫은 경험치 못 얻음

        self.experience += exp_gain
        leveled_up = False

        while self.experience >= 100:
            if self.level < 10:
                self.experience -= 100
                self.level += 1
                leveled_up = True
            else:
                # ✅ 레벨 10이면 자연사 처리
                self.experience = 0
                self.set_pet_status("aged")
                return True

        self.save()
        return leveled_up
    


    def play_with_toy(self, inventory, toy_type):
        """✅ 장난감 사용 시 경험치 증가 및 체력 감소"""
        if toy_type not in ["toy1", "toy2", "toy3"]:
            return False, "잘못된 장난감 유형입니다."
        if getattr(inventory, toy_type) <= 0:
            return False, f"{toy_type}이 부족합니다."
        if self.health <= 0:
            return False, "펫의 체력이 부족합니다."

         # 기본 경험치 증가량 (레벨이 높을수록 경험치 증가량 감소)
        exp_gain = max(10 - (self.level - 1), 1)

        # 체력이 100 이상이면 경험치 2배 증가
        if self.health >= 100:
            exp_gain *= 2

        # 체력 소모: 5만큼 감소 (최소 0)
        self.health = max(self.health - 5, 0)
        # 장난감 개수 감소 후 저장
        setattr(inventory, toy_type, getattr(inventory, toy_type) - 1)
        inventory.save()

        # 경험치 증가 및 레벨업 여부 판단
        leveled_up = self.gain_experience(exp_gain)
        if leveled_up:
            message = f"{self.name}의 레벨이 {self.level}이 되었습니다! 축하합니다!"
        else:
            message = f"펫이 장난감으로 놀았습니다! (+{exp_gain} 경험치)"

        return leveled_up, message



    def level_up(self):
        """ ✅ 경험치가 100 이상이면 레벨업 처리 """
        if self.experience >= 100 and self.level < 10:  # ✅ 경험치 100 이상 확인
            self.level += 1
            self.experience = 0
            self.save()


    def reduce_experience_over_time(self):
        """ ✅ 시간이 지날수록 체력 감소, 체력 0이면 사망 처리 """
        if not self.is_active_pet():
            return

        now = timezone.now()

        while self.last_activity + timedelta(hours=1) <= now:
            self.health = max(self.health - 1, 0)
            self.last_activity += timedelta(hours=1)

        if self.health <= 0:
            self.set_pet_status("neglected")  # ✅ 체력이 0이면 관리 부족으로 사망 처리

        self.save()
