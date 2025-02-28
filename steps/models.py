# steps/models.py
from django.db import models
from django.contrib.auth.models import User

class StepCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자 정보
    date = models.DateField(auto_now_add=True)  # 걸음 수 기록 날짜
    steps = models.IntegerField()  # 걸음 수 데이터

    def __str__(self):
        return f"{self.user.username} - {self.steps} steps on {self.date}"
