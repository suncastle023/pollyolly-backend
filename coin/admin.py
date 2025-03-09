from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from coin.models import Coin

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "pending_coins",
        "pending_feed",
        "pending_toy",
        "total_pending_rewards",  # ✅ 보류 보상 개수 한눈에 보기
        "last_rewarded_steps",
        "last_reward_date",
        "display_pending_rewards",  # ✅ 보류된 보상 HTML로 표시
        "clear_rewards_button",  # ✅ 보류 보상을 초기화하는 버튼 추가
    )

    list_filter = ("last_reward_date",)
    search_fields = ("user__email", "user__nickname")

    fieldsets = (
        ("유저 정보", {"fields": ("user",)}),
        ("코인 정보", {"fields": ("amount", "pending_coins", "pending_feed", "pending_toy")}),
        ("보상 기록", {"fields": ("last_rewarded_steps", "last_reward_date")}),
        ("Pending Rewards 상세", {"fields": ("display_pending_rewards",)}),
    )

    readonly_fields = ("display_pending_rewards",)

    def total_pending_rewards(self, obj):
        """보류된 보상의 총 개수를 표시"""
        return len(obj.pending_rewards) if obj.pending_rewards else 0

    total_pending_rewards.short_description = "보류 보상 개수"

    def display_pending_rewards(self, obj):
        """Pending Rewards를 보기 쉽게 HTML 리스트로 변환"""
        if not hasattr(obj, "pending_rewards") or not obj.pending_rewards:
            return "No pending rewards"

        formatted_rewards = "<ul>"
        for i, reward in enumerate(obj.pending_rewards):
            formatted_rewards += f"<li>🆕 {i+1}번째 보상 - Feed: {reward.get('feed', 0)}, Toy: {reward.get('toy', 0)}</li>"
        formatted_rewards += "</ul>"

        return mark_safe(formatted_rewards)

    display_pending_rewards.short_description = "Pending Rewards (랜덤 보상 기록)"

    def clear_rewards_button(self, obj):
        """보류된 보상을 초기화하는 버튼 추가"""
        return format_html(
            '<a class="button" href="{}">🧹 보류 보상 초기화</a>',
            f"clear-pending-rewards/{obj.pk}/"
        )

    clear_rewards_button.short_description = "보류 보상 초기화"

    def get_readonly_fields(self, request, obj=None):
        """슈퍼유저는 모든 필드를 수정 가능, 일반 유저는 일부 필드만 읽기 전용"""
        if request.user.is_superuser:
            return []  # ✅ 슈퍼유저는 모든 필드를 수정 가능
        return (
            "pending_coins",
            "pending_feed",
            "pending_toy",
            "last_rewarded_steps",
            "last_reward_date",
            "display_pending_rewards",
        )

    def get_urls(self):
        """어드민 커스텀 URL 추가 (보류 보상 초기화 기능)"""
        urls = super().get_urls()
        custom_urls = [
            path("clear-pending-rewards/<int:coin_id>/", self.clear_pending_rewards, name="clear_pending_rewards"),
        ]
        return custom_urls + urls

    def clear_pending_rewards(self, request, coin_id):
        """보류된 보상을 모두 초기화하는 기능"""
        coin = Coin.objects.get(pk=coin_id)
        coin.pending_coins = 0
        coin.pending_feed = 0
        coin.pending_toy = 0
        coin.pending_rewards = []
        coin.save()

        messages.success(request, f"{coin.user}님의 보류된 보상이 초기화되었습니다!")
        return redirect(request.META.get("HTTP_REFERER", "/admin/coin/coin/"))
