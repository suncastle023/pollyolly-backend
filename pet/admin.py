from django.contrib import admin
from .models import Pet

class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "pet_type", "breed", "level", "experience", "last_activity")
    list_filter = ("pet_type", "level")
    search_fields = ("name", "owner__email")  # 🔥 사용자 이메일 검색 가능
    ordering = ("level", "experience")

admin.site.register(Pet, PetAdmin)
