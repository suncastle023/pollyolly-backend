from django.db import models
from django.conf import settings
import random
from datetime import timedelta
from django.utils import timezone

class Pet(models.Model):
    PET_TYPES = {
        "강아지": ["시바견", "리트리버", "푸들","베니"],
        "고양이": ["러시안 블루", "샴", "먼치킨"],
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
        "러시안 블루": "assets/pet_images/russian_blue.png",
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
    experience = models.IntegerField(default=50) 
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
        """ ✅ 사료 사용하여 체력(경험치) 회복 """
        if inventory.feed > 0:
            self.experience = min(self.experience + 10, 100)  
            inventory.feed -= 1
            inventory.save()
            self.save()

            if self.experience >= 100:  # ✅ 경험치 100 이상이면 레벨업 호출
                self.level_up()

            return True
        if inventory.water > 0:
            self.experience = min(self.experience + 5, 100)
            inventory.water -= 1
            inventory.save()
            self.save()

            if self.experience >= 100:  # ✅ 경험치 100 이상이면 레벨업 호출
                self.level_up()

            return True
        return False


    def play_with_toy(self, inventory):
        """ ✅ 장난감 사용 시 체력 감소 및 경험치 증가 """
        if inventory.toy > 0 and self.experience > 0:
            exp_gain = max(10 - (self.level - 1), 1)  # 레벨이 높을수록 경험치 증가량 감소
            self.experience = max(self.experience - 5, 0)  # 체력 감소 (0 이하 불가)
            self.experience += exp_gain
            inventory.toy -= 1
            inventory.save()
            self.save()

            if self.experience >= 100:  # ✅ 체력이 가득 차면 레벨업
                self.level_up()
            return True
        return False

    def level_up(self):
        """ ✅ 경험치가 100 이상이면 레벨업 처리 """
        if self.experience >= 100 and self.level < 10:  # ✅ 경험치 100 이상 확인
            self.level += 1
            self.experience = 50  # 레벨업 후 체력 절반 유지
            self.save()


    def reduce_experience_over_time(self):
        """ ✅ 1시간마다 경험치 0.5 감소 """
        now = timezone.now()
        if self.last_activity is None:
            self.last_activity = now  # 처음 활동 시간이 없으면 현재 시간으로 설정
        hours_passed = (now - self.last_activity).total_seconds() // 3600  # 경과 시간(시간 단위)

        if hours_passed >= 1:
            self.experience = max(self.experience - (0.5 * hours_passed), 0)
            self.last_activity = now  # ✅ 업데이트 시간 저장
            self.save()
