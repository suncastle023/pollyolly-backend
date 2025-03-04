from django.db import models
from django.conf import settings

class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(max_length=10, choices=[("pending", "대기중"), ("accepted", "수락됨"), ("rejected", "거절됨")], default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')  # 같은 친구 요청 중복 방지

    def __str__(self):
        return f"{self.sender.nickname} → {self.receiver.nickname} ({self.status})"

class Friend(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friends")
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friend_of")
    created_at = models.DateTimeField(auto_now_add=True)  # 친구 추가 시간

    class Meta:
        unique_together = ('user', 'friend')  # 중복 친구 추가 방지

    def __str__(self):
        return f"{self.user.nickname} ↔ {self.friend.nickname}"
