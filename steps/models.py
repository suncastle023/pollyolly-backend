from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class StepCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    step_count = models.PositiveIntegerField()

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.step_count} steps"
