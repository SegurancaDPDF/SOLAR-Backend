# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers


# define as views para manipulação do modelo 'Formulario'
class FormularioViewSet(ModelViewSet):
    queryset = models.Formulario.objects.all()
    serializer_class = serializers.FormularioSerializer


# define as views para manipulação do modelo 'Nucleo'
class NucleoViewSet(ModelViewSet):
    queryset = models.Nucleo.objects.all()
    serializer_class = serializers.NucleoSerializer


# define as views para manipulação do modelo 'Pergunta'
class PerguntaViewSet(ModelViewSet):
    queryset = models.Pergunta.objects.all()
    serializer_class = serializers.PerguntaSerializer


# define as views para manipulação do modelo 'Resposta'
class RespostaViewSet(ModelViewSet):
    queryset = models.Resposta.objects.all()
    serializer_class = serializers.RespostaSerializer
