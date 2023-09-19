# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models, serializers


class AlertaProcessoMovimentoViewSet(ModelViewSet):
    queryset = models.AlertaProcessoMovimento.objects.all()
    serializer_class = serializers.AlertaProcessoMovimentoSerializer


class AnaliseViewSet(ModelViewSet):
    queryset = models.Analise.objects.all()
    serializer_class = serializers.AnaliseSerializer


class DocumentoViewSet(ModelViewSet):
    queryset = models.Documento.objects.all()
    serializer_class = serializers.DocumentoSerializer


class HonorarioViewSet(ModelViewSet):
    queryset = models.Honorario.objects.all()
    serializer_class = serializers.HonorarioSerializer


class MovimentoViewSet(ModelViewSet):
    queryset = models.Movimento.objects.all()
    serializer_class = serializers.MovimentoSerializer
