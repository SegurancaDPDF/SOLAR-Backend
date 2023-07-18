# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers


class TermoViewSet(ModelViewSet):
    queryset = models.Termo.objects.all()
    serializer_class = serializers.TermoSerializer


class TermoRespostaViewSet(ModelViewSet):
    queryset = models.TermoResposta.objects.all()
    serializer_class = serializers.TermoRespostaSerializer
