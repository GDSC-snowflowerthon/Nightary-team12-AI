from rest_framework import viewsets
from .models import SleepData
from .serializers import SleepDataSerializer
from .services import process_sleep_data 
from rest_framework.response import Response

class SleepDataViewSet(viewsets.ModelViewSet):
    queryset = SleepData.objects.all()
    serializer_class = SleepDataSerializer

    def create(self, request, *args, **kwargs):
        response = process_sleep_data(request.data)
        return Response(response)