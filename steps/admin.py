from django.contrib import admin
from .models import StepCount

@admin.register(StepCount)
class StepCountAdmin(admin.ModelAdmin):
    list_display = ('user', 'steps', 'date')  # ✅ Admin 패널에서 보이는 필드
    search_fields = ('user__email',)  # ✅ 이메일로 검색 가능
    list_filter = ('date',)  # ✅ 날짜별 필터링 가능

