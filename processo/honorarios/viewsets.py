# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers


# viewset que gerencia as operações CRUD para o modelo AlertaProcessoMovimento
class AlertaProcessoMovimentoViewSet(ModelViewSet):
    queryset = models.AlertaProcessoMovimento.objects.all()
    serializer_class = serializers.AlertaProcessoMovimentoSerializer


# viewset que gerencia as operações CRUD para o modelo Analise
class AnaliseViewSet(ModelViewSet):
    queryset = models.Analise.objects.all()
    serializer_class = serializers.AnaliseSerializer


# viewset que gerencia as operações CRUD para o modelo Documento
class DocumentoViewSet(ModelViewSet):
    queryset = models.Documento.objects.all()
    serializer_class = serializers.DocumentoSerializer


# viewset que gerencia as operações CRUD para o modelo Honorario
class HonorarioViewSet(ModelViewSet):
    queryset = models.Honorario.objects.all()
    serializer_class = serializers.HonorarioSerializer


# viewset que gerencia as operações CRUD para o modelo Movimento
class MovimentoViewSet(ModelViewSet):
    queryset = models.Movimento.objects.all()
    serializer_class = serializers.MovimentoSerializer
