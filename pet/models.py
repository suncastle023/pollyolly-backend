from django.db import models
from django.conf import settings
import random
from datetime import timedelta
from django.utils import timezone

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
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=50)  # ✅ 체력(경험치) 역할 수행
    last_activity = models.DateTimeField(auto_now_add=True)  # ✅ 마지막 활동 시간 기록

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
        """ ✅ 사료나 물을 사용하여 체력(경험치) 회복 """
        if inventory.food > 0:
            self.experience = min(self.experience + 10, 100)  # 최대 체력(100) 초과 불가
            inventory.food -= 1
            inventory.save()
            self.save()
            return True
        if inventory.water > 0:
            self.experience = min(self.experience + 5, 100)
            inventory.water -= 1
            inventory.save()
            self.save()
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
        """ ✅ 체력이 100일 때 레벨업 처리 """
        if self.level < 10:
            self.level += 1
            self.experience = 50  # 레벨업 후 체력 절반 유지
            self.save()

    def reduce_experience_over_time(self):
        """ ✅ 1시간마다 체력(경험치) 0.5 감소 """
        now = timezone.now()
        hours_passed = (now - self.last_activity).total_seconds() // 3600  # 경과 시간(시간 단위)

        if hours_passed >= 1:
            self.experience = max(self.experience - (0.5 * hours_passed), 0)
            self.last_activity = now
            self.save()
