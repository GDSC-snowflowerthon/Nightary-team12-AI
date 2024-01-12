from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PredictViewSet, AnalyzeViewSet

router = DefaultRouter()
router.register(r'predict', PredictViewSet)
router.register(r'analyze', AnalyzeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]