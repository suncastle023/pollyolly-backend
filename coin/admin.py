from django.contrib import admin
from coin.models import Coin

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "last_rewarded_steps", "last_reward_date", "total_feed_bonus", "total_toy_bonus")
    list_filter = ("last_reward_date",)
    search_fields = ("user__email", "user__username")
    readonly_fields = ("last_rewarded_steps", "last_reward_date", "total_feed_bonus", "total_toy_bonus")

    # ✅ 슈퍼유저가 코인 수량을 조정할 수 있도록 설정
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []  # 슈퍼유저는 모든 필드를 수정 가능
        return self.readonly_fields
    
