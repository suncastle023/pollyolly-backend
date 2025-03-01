from rest_framework import serializers
from .models import Pet

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ['id', 'owner', 'name', 'pet_type', 'breed', 'level', 'experience']  # ✅ 경험치 추가
        read_only_fields = ['owner', 'pet_type', 'breed', 'level', 'experience']  # ✅ 경험치도 읽기 전용
