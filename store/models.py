from django.db import models
from django.conf import settings

class Item(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('toy', 'Toy'),
        ('water', 'Water'),
        ('background', 'Background'),
        ('house', 'House'),
    ]

    ITEM_PRICES = {
        "feed": 3,
        "pm_feed": 6,
        "toy": 1,
        "pm_toy": 2,
        "water": 2,
        "pm_water": 4,
        "default_bg": 10,
        "default_bg2": 50,
        "box": 0,
        "cat_tower": 100,
        "dog_home": 100,
        "home1": 200,
        "home2": 200,
        "pet_home": 300,
        "short_tree": 140,
        "tent": 50,
    }

    name = models.CharField(max_length=50, unique=True)
    price = models.IntegerField(blank=True, null=True)  # 자동 설정됨
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def save(self, *args, **kwargs):
        """아이템 생성 시 자동으로 price 값 설정"""
        if self.price is None:
            self.price = self.ITEM_PRICES.get(self.name, 10)  # 기본값 10
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.price} 코인"


class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    coins = models.IntegerField(default=10)  # 기본 코인 지급
