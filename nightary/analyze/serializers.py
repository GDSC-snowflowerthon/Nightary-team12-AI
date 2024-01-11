from rest_framework import serializers
from .models import SleepData

class SleepDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepData
        fields = ['start_sleep_date', 'end_sleep_date', 'sleep_duration']
