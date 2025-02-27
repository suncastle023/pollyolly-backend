from django.db import models
from django.conf import settings
import random

class Pet(models.Model):
    PET_TYPES = {
        "강아지": ["시바견", "리트리버", "푸들"],
        "고양이": ["러시안 블루", "샴", "먼치킨"],
        "토끼": ["토끼"],
        "햄스터": ["햄스터"],
        "거북이": ["거북이"],
        "앵무새": ["앵무새"],
        "물고기": ["금붕어", "베타피쉬"],
        "미니 요괴": ["꼬리가 여러 개인 여우"],
        "그리폰": ["그리폰"],
        "유니콘": ["유니콘"],
        "드래곤": ["아기 드래곤", "미니 드래곤"],
        "불사조": ["피닉스"],
    }

    LEVEL_UNLOCKS = [
        (1, ["강아지", "고양이"]),
        (4, ["햄스터", "물고기"]),
        (11, ["앵무새", "거북이"]),
        (20, ["미니 요괴"]),
        (26, ["그리폰"]),
        (31, ["유니콘"]),
        (41, ["드래곤"]),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=20)
    breed = models.CharField(max_length=20)
    level = models.IntegerField(default=1)  # 반려동물 레벨 (1~10)

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
