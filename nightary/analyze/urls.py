from . import views
from django.urls import path

urlpatterns=[
    path('predict-sleep/',views.sleep_prediction,name='sleep_prediction'),
]