from django.db import models
from django.conf import settings
import random
from datetime import timedelta
from django.utils import timezone

class Pet(models.Model):
    PET_TYPES = {
        "강아지": ["시바견", "리트리버", "푸들","베니"],
        "고양이": ["러시안블루", "샴", "먼치킨"],
        "토끼": ["핑크토끼"],
        "햄스터": ["햄스터"],
        "거북이": ["거북이"],
        "새": ["앵무새"],
        "물고기": ["금붕어", "열대어"],
        "요괴": ["구미호","해치","불사조"],
        "그리폰": ["그리폰"],
        "유니콘": ["유니콘"],
        "드래곤": ["드래곤"],
    }

    LEVEL_UNLOCKS = [
        (1, ["강아지", "고양이"]),
        (4, ["햄스터", "물고기"]),
        (11, ["새", "거북이"]),
        (20, ["그리폰"]),
        (26, ["요괴"]),
        (31, ["유니콘"]),
        (41, ["드래곤"]),
    ]

    IMAGE_PATHS = {
        "베니": "assets/pet_images/benny_sad.png",
        "시바견": "assets/pet_images/shiba_inu.png",
        "리트리버": "assets/pet_images/retriever.png",
        "푸들": "assets/pet_images/poodle.png",
        "러시안블루": "assets/pet_images/russian_blue.png",
        "샴": "assets/pet_images/siamese.png",
        "먼치킨": "assets/pet_images/munchkin.png",
        "핑크토끼": "assets/pet_images/rabbit.png",
        "햄스터": "assets/pet_images/hamster.png",
        "거북이": "assets/pet_images/turtle.png",
        "앵무새": "assets/pet_images/parrot.png",
        "금붕어": "assets/pet_images/gold_fish.png",
        "열대어": "assets/pet_images/tropical_fish.png",
        "구미호": "assets/pet_images/ninetail.png",
        "해치": "assets/pet_images/hatch.png",
        "불사조": "assets/pet_images/phoenix.png",
        "그리폰": "assets/pet_images/griffon.png",
        "유니콘": "assets/pet_images/unicorn.png",
        "드래곤": "assets/pet_images/dragon.png",
    }

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=20)
    breed = models.CharField(max_length=20)
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0) 
    health = models.IntegerField(default=50)
    last_activity = models.DateTimeField(default=timezone.now) 
    image_path = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        """자동으로 이미지 경로 설정"""
        if self.breed in self.IMAGE_PATHS:
            self.image_path = self.IMAGE_PATHS[self.breed]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.breed}) - Lv.{self.level}"

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

    def feed_pet(self, inventory):
        """ 사료 또는 물 사용 시 체력 회복 """
        if inventory.feed > 0:
            self.health = min(self.health + 10, 300)
            inventory.feed -= 1
            inventory.save()
            self.save()
            return False  # 경험치 변화 없음

        if inventory.water > 0:
            self.health = min(self.health + 30, 300)
            inventory.water -= 1
            inventory.save()
            self.save()
            return False  # 경험치 변화 없음

        return False


    def gain_experience(self, exp_gain):
        """
        경험치를 증가시키고, 경험치가 100 이상이면 레벨업을 자동으로 처리하는 함수.
        """
        self.experience += exp_gain
        leveled_up = False

        # 경험치가 100 이상이면 레벨업
        while self.experience >= 100 and self.level < 10:
            self.experience -= 100
            self.level += 1
            leveled_up = True

        self.save()
        return leveled_up
    

    def play_with_toy(self, inventory):
        """ 장난감 사용 시 경험치 증가 및 체력 감소 """
        if inventory.toy > 0 and self.health > 0:
            exp_gain = max(10 - (self.level - 1), 1)  # 레벨이 높을수록 경험치 감소
            self.health = max(self.health - 5, 0)  # 체력 감소
            inventory.toy -= 1
            inventory.save()

            # 경험치 증가 및 레벨업 여부 체크
            return self.gain_experience(exp_gain)
        return False
    


    def level_up(self):
        """ ✅ 경험치가 100 이상이면 레벨업 처리 """
        if self.experience >= 100 and self.level < 10:  # ✅ 경험치 100 이상 확인
            self.level += 1
            self.experience = 0
            self.save()


    def reduce_experience_over_time(self):
        now = timezone.now()

        # last_activity가 None이면 현재 시간으로 초기화
        if self.last_activity is None:
            self.last_activity = now

        # last_activity가 now보다 작으면, 1시간씩 증가시키면서 체력을 깎는다.
        while self.last_activity + timedelta(hours=1) <= now:
            self.health = max(self.health - 1, 0)  # 시간당 체력 1 감소
            self.last_activity += timedelta(hours=1)

        self.save()
