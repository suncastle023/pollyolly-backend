# steps/models.py
from django.db import models
from django.conf import settings  # ✅ 현재 사용 중인 사용자 모델 가져오기

class StepCount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ CustomUser 사용
    date = models.DateField(auto_now_add=True)  # 걸음 수 기록 날짜
    steps = models.IntegerField()  # 걸음 수 데이터

    def __str__(self):
        return f"{self.user.username} - {self.steps} steps on {self.date}"
