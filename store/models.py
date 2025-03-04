from django.db import models
from django.conf import settings  

class Item(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.IntegerField()

class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    coins = models.IntegerField(default=10)  # 기본 코인 지급
