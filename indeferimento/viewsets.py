# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers


# define as operacoes de visualizacao e manipulacao dos objetos de Indeferimento
class IndeferimentoViewSet(ModelViewSet):
    queryset = models.Indeferimento.objects.all()
    serializer_class = serializers.IndeferimentoSerializer
