from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Inventory

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_inventory(sender, instance, created, **kwargs):
    if created:
        inventory = Inventory.objects.create(user=instance)
        # 인벤토리 생성 시 기본으로 배경/집 아이템이 추가되는 것을 방지하기 위해
        # 해당 ManyToManyField를 명시적으로 비워둡니다.
        inventory.backgrounds.clear()
        inventory.houses.clear()
