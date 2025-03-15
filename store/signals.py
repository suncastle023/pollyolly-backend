from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Item

@receiver(post_migrate)
def create_default_items(sender, **kwargs):
    """마이그레이션 후 자동으로 기본 아이템 추가"""
    if sender.name == "store":  # store 앱이 마이그레이션될 때만 실행
        default_items = [
            {"name": "feed", "price": 3, "category": "food"},
            {"name": "pm_feed", "price": 6, "category": "food"},
            {"name": "water", "price": 2, "category": "water"},
            {"name": "pm_water", "price": 4, "category": "water"},
            {"name": "toy1", "price": 1, "category": "toy"},
            {"name": "toy2", "price": 2, "category": "toy"},
            {"name": "toy3", "price": 3, "category": "toy"},
            {"name": "default_bg", "price": 50, "category": "background"},
            {"name": "default_bg2", "price": 10, "category": "background"},
            {"name": "box", "price": 0, "category": "house"},
            {"name": "cat_tower", "price": 100, "category": "house"},
            {"name": "dog_home", "price": 100, "category": "house"},
            {"name": "home1", "price": 200, "category": "house"},
            {"name": "home2", "price": 200, "category": "house"},
            {"name": "pet_home", "price": 300, "category": "house"},
            {"name": "short_tree", "price": 140, "category": "house"},
            {"name": "tent", "price": 50, "category": "house"},
        ]

        for item_data in default_items:
            Item.objects.get_or_create(name=item_data["name"], defaults=item_data)

        print("✅ 기본 아이템 데이터가 자동으로 추가되었습니다.")
