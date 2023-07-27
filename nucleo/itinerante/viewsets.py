# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers


class EventoViewSet(ModelViewSet):
    queryset = models.Evento.objects.all()
    serializer_class = serializers.EventoSerializer
