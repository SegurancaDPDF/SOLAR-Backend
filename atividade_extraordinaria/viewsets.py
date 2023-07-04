# third-party
# Importações necessárias
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers

# Classe responsável por fornecer as funcionalidades de visualização, criação, atualização e exclusão
# Os atributos `queryset` e `serializer_class` indica o conjunto de dados e o serializador a serem usados.


class AtividadeExtraordinariaTipoViewSet(ModelViewSet):
    queryset = models.AtividadeExtraordinariaTipo.objects.all()
    serializer_class = serializers.AtividadeExtraordinariaTipoSerializer


class AtividadeExtraordinariaViewSet(ModelViewSet):
    queryset = models.AtividadeExtraordinaria.objects.all()
    serializer_class = serializers.AtividadeExtraordinariaSerializer
