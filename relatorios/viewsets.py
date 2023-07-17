# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import filters
from . import models
from . import serializers


class LocalViewSet(ModelViewSet):
    queryset = models.Local.objects.all()
    serializer_class = serializers.LocalSerializer


class RelatorioViewSet(ModelViewSet):
    queryset = models.Relatorio.objects.all()
    serializer_class = serializers.RelatorioSerializer
    filter_class = filters.RelatorioFilter
