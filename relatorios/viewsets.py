# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import filters
from . import models
from . import serializers


class LocalViewSet(ModelViewSet):
    queryset = models.Local.objects.all()  # consulta inicial para a model 'Local', retornando todas as instâncias
    serializer_class = serializers.LocalSerializer


class RelatorioViewSet(ModelViewSet):
    queryset = models.Relatorio.objects.all()  # consulta inicial para a model 'Relatorio', retornando todas instâncias
    serializer_class = serializers.RelatorioSerializer
    filter_class = filters.RelatorioFilter
