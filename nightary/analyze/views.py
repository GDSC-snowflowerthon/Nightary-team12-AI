from rest_framework import viewsets
from .models import SleepData
from .serializers import SleepDataSerializer
from .services import predict_sleep_data , analyze_sleep_data
from django.http import JsonResponse

class PredictViewSet(viewsets.ModelViewSet):
    queryset = SleepData.objects.all()
    serializer_class = SleepDataSerializer

    def create(self, request, *args, **kwargs):
        response = predict_sleep_data(request.data)
        return JsonResponse(response)

class AnalyzeViewSet(viewsets.ModelViewSet):
    queryset = SleepData.objects.all()
    serializer_class = SleepDataSerializer

    def create(self, request, *args, **kwargs):
        response = analyze_sleep_data(request.data)
        return JsonResponse(response)