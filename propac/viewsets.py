# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import models
from . import serializers


class DocumentoPropacViewSet(ModelViewSet):  # define um viewset para a entidade documentopropac
    queryset = models.DocumentoPropac.objects.all()
    serializer_class = serializers.DocumentoPropacSerializer


class MovimentoViewSet(ModelViewSet):  # define um viewset para a entidade movimento
    queryset = models.Movimento.objects.all()
    serializer_class = serializers.MovimentoSerializer


class MovimentoTipoViewSet(ModelViewSet):  # define um viewset para a entidade movimentotipo
    queryset = models.MovimentoTipo.objects.all()
    serializer_class = serializers.MovimentoTipoSerializer


class ProcedimentoViewSet(ModelViewSet):  # define um viewset para a entidade procedimento
    queryset = models.Procedimento.objects.all()
    serializer_class = serializers.ProcedimentoSerializer


class SituacaoProcedimentoViewSet(ModelViewSet):  # define um viewset para a entidade situacaoprocedimento
    queryset = models.SituacaoProcedimento.objects.all()
    serializer_class = serializers.SituacaoProcedimentoSerializer


class TipoAnexoDocumentoPropacViewSet(ModelViewSet):  # define um viewset para a entidade tipoanexodocumentopropac
    queryset = models.TipoAnexoDocumentoPropac.objects.all()
    serializer_class = serializers.TipoAnexoDocumentoPropacSerializer
