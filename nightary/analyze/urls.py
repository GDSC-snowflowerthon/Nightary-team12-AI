from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SleepDataViewSet

router = DefaultRouter()
router.register(r'sleepdata', SleepDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
]