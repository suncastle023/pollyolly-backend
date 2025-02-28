# steps/serializers.py
from rest_framework import serializers
from .models import StepCount

class StepCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepCount
        fields = ['id', 'user', 'date', 'steps']
        read_only_fields = ['user', 'date']  # 유저와 날짜는 자동으로 설정됨
