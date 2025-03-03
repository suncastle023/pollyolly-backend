from django.contrib import admin
from .models import StepCount

@admin.register(StepCount)
class StepCountAdmin(admin.ModelAdmin):
    list_display = ('user', 'steps', 'date')  # ✅ 'owner' 대신 'user' 사용
    search_fields = ('user__email',)  # ✅ 'email' 대신 'user__email'로 수정
    list_filter = ('date',)  # ✅ 날짜별 필터링 가능
