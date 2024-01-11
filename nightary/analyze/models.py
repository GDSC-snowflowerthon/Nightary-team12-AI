from django.db import models

class SleepData(models.Model):
    start_sleep_date = models.DateTimeField()
    end_sleep_date = models.DateTimeField()
    sleep_duration = models.FloatField() 
