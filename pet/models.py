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
        "dog": ["shiba_inu", "retriever", "poodle", "benny_sad", "polly"],
        "cat": ["russian_blue", "siamese", "munchkin"],
        "rabbit": ["rabbit"],
        "hamster": ["hamster"],
        "turtle": ["turtle"],
        "bird": ["parrot"],
        "fish": ["gold_fish", "tropical_fish"],
        "yokai": ["ninetail", "hatch", "phoenix"],
        "griffon": ["griffon"],
        "unicorn": ["unicorn"],
        "dragon": ["dragon"],
    }

    LEVEL_UNLOCKS = [
        (1, ["dog", "cat"]),
        (4, ["hamster", "fish"]),
        (11, ["bird", "turtle"]),
        (20, ["griffon"]),
        (26, ["yokai"]),
        (31, ["unicorn"]),
        (41, ["dragon"]),
    ]


    IMAGE_PATHS = {
        "polly": "assets/pet_images/polly.png",
        "pollyL": "assets/pet_images/pollyL.png",
        "pollyR": "assets/pet_images/pollyR.png",
        "dirty_polly": "assets/pet_images/dirty_polly.png",
        "dirty_pollyL": "assets/pet_images/dirty_pollyL.png",
        "dirty_pollyR": "assets/pet_images/dirty_pollyR.png",
        "benny_sad": "assets/pet_images/benny_sad.png",
        "shiba_inu": "assets/pet_images/shiba_inu.png",
        "retriever": "assets/pet_images/retriever.png",
        "poodle": "assets/pet_images/poodle.png",
        "russian_blue": "assets/pet_images/russian_blue.png",
        "siamese": "assets/pet_images/siamese.png",
        "munchkin": "assets/pet_images/munchkin.png",
        "rabbit": "assets/pet_images/rabbit.png",
        "hamster": "assets/pet_images/hamster.png",
        "turtle": "assets/pet_images/turtle.png",
        "parrot": "assets/pet_images/parrot.png",
        "gold_fish": "assets/pet_images/gold_fish.png",
        "tropical_fish": "assets/pet_images/tropical_fish.png",
        "ninetail": "assets/pet_images/ninetail.png",
        "hatch": "assets/pet_images/hatch.png",
        "phoenix": "assets/pet_images/phoenix.png",
        "griffon": "assets/pet_images/griffon.png",
        "unicorn": "assets/pet_images/unicorn.png",
        "dragon": "assets/pet_images/dragon.png",
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
        """ ✅ 장난감 사용 시 경험치 증가 및 체력 감소 """
        if toy_type not in ["toy1", "toy2", "toy3"]:
            return False, "잘못된 장난감 유형입니다."
        if getattr(inventory, toy_type) <= 0:
            return False, f"{toy_type}이 부족합니다."
        if self.health <= 0:
            return False, "펫의 체력이 부족합니다."

        exp_gain = max(10 - (self.level - 1), 1)  # ✅ 레벨이 높을수록 경험치 감소
        self.health = max(self.health - 5, 0)  # ✅ 체력 소모
        setattr(inventory, toy_type, getattr(inventory, toy_type) - 1)  # ✅ 장난감 개수 감소
        inventory.save()

        return self.gain_experience(exp_gain), "펫이 장난감으로 놀았습니다!"



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

        if self.health == 0:
            self.set_pet_status("neglected")  # ✅ 체력이 0이면 관리 부족으로 사망 처리

        self.save()
