from django.db import models
from django.conf import settings

class StepCount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    step_count = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.step_count} steps on {self.date}"
