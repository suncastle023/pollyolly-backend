from django.contrib import admin
from django.utils.safestring import mark_safe
from coin.models import Coin

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "pending_coins",
        "pending_feed",
        "pending_toy",
        "last_rewarded_steps",
        "last_reward_date",
        "display_pending_rewards"
    )

    list_filter = ("last_reward_date",)
    search_fields = ("user__email", "user__username")

    fieldsets = (
        ("유저 정보", {"fields": ("user",)}),
        ("코인 정보", {"fields": ("amount", "pending_coins", "pending_feed", "pending_toy")}),

        ("보상 기록", {"fields": ("last_rewarded_steps", "last_reward_date")}),

        ("Pending Rewards 상세", {"fields": ("display_pending_rewards",)}),
    )

    def display_pending_rewards(self, obj):
        """Pending Rewards를 HTML 리스트로 보여줌"""
        if not obj.pending_rewards:
            return "No pending rewards"

        formatted_rewards = "<ul>"
        for reward in obj.pending_rewards:
            formatted_rewards += f"<li>Feed: {reward.get('feed', 0)}, Toy: {reward.get('toy', 0)}</li>"
        formatted_rewards += "</ul>"

        return mark_safe(formatted_rewards)

    display_pending_rewards.short_description = "Pending Rewards (랜덤 보상 기록)"

    def get_readonly_fields(self, request, obj=None):
        """슈퍼유저는 모든 필드를 수정 가능, 일반 유저는 일부 필드만 읽기 전용"""
        if request.user.is_superuser:
            return []  
        return (
            "pending_coins",
            "pending_feed",
            "pending_toy",
            "last_rewarded_steps",
            "last_reward_date",
            "display_pending_rewards"
        )
