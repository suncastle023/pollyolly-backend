from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Inventory

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_inventory(sender, instance, created, **kwargs):
    if created:
        Inventory.objects.create(user=instance)
