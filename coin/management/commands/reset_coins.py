from django.core.management.base import BaseCommand
from django.utils import timezone
from coin.models import Coin

class Command(BaseCommand):
    help = "매일 자정에 pending_coins 및 last_rewarded_steps를 초기화합니다."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        updated_count = Coin.objects.update(
            pending_coins=0,
            pending_feed=0,
            pending_toy=0,
            last_rewarded_steps=0,
            last_reward_date=today
        )
        self.stdout.write(self.style.SUCCESS(f"✅ {updated_count}명의 코인 정보가 초기화되었습니다."))
