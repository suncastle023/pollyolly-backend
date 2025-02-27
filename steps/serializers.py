from rest_framework import serializers
from .models import StepCount

class StepCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepCount
        fields = ['id', 'user', 'date', 'step_count']
        read_only_fields = ['user', 'date']
