from django.contrib import admin
from .models import Item, UserProfile

class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price")  # 존재하는 필드만 사용
    search_fields = ("name",)  # 아이템 이름 검색 가능
    ordering = ("price",)  # 가격 기준 정렬

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "coins")  # 유저와 코인 보이기
    search_fields = ("user__username",)  # 유저 검색 가능
    ordering = ("coins",)  # 코인 기준 정렬

admin.site.register(Item, ItemAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
