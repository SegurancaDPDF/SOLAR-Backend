# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import filters
from . import models
from . import serializers


class GuicheViewSet(ModelViewSet):
    queryset = models.Guiche.objects.all()
    serializer_class = serializers.GuicheSerializer


class PredioViewSet(ModelViewSet):
    queryset = models.Predio.objects.all()
    serializer_class = serializers.PredioSerializer
    filter_class = filters.PredioFilter
