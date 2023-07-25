# third-party
from rest_framework.viewsets import ModelViewSet

# application
from . import filters
from . import models
from . import serializers


# representa uma viewset para o recurso processoapenso
class ProcessoApensoViewSet(ModelViewSet):
    queryset = models.ProcessoApenso.objects.all()
    serializer_class = serializers.ProcessoApensoSerializer


# representa uma viewset para o recurso acao
class AcaoViewSet(ModelViewSet):
    queryset = models.Acao.objects.all()
    serializer_class = serializers.AcaoSerializer


# representa uma viewset para o recurso assunto
class AssuntoViewSet(ModelViewSet):
    queryset = models.Assunto.objects.all()
    serializer_class = serializers.AssuntoSerializer


# representa uma viewset para o recurso audiencia
class AudienciaViewSet(ModelViewSet):
    queryset = models.Audiencia.objects.all()
    serializer_class = serializers.AudienciaSerializer
    filter_class = filters.AudienciaFilter


# representa uma viewset para o recurso manifestacaoaviso
class ManifestacaoAvisoViewSet(ModelViewSet):
    queryset = models.ManifestacaoAviso.objects.all()
    serializer_class = serializers.ManifestacaoAvisoSerializer


# representa uma viewset para o recurso documentofase
class DocumentoFaseViewSet(ModelViewSet):
    queryset = models.DocumentoFase.objects.all()
    serializer_class = serializers.DocumentoFaseSerializer


class ManifestacaoDocumentoViewSet(ModelViewSet):
    queryset = models.ManifestacaoDocumento.objects.all()
    serializer_class = serializers.ManifestacaoDocumentoSerializer


class FaseViewSet(ModelViewSet):
    queryset = models.Fase.objects.all()
    serializer_class = serializers.FaseSerializer


class ParteHistoricoTransferenciaViewSet(ModelViewSet):
    queryset = models.ParteHistoricoTransferencia.objects.all()
    serializer_class = serializers.ParteHistoricoTransferenciaSerializer


class ManifestacaoViewSet(ModelViewSet):
    queryset = models.Manifestacao.objects.all()
    serializer_class = serializers.ManifestacaoSerializer
    filter_class = filters.ManifestacaoFilter


class OutroParametroViewSet(ModelViewSet):
    queryset = models.OutroParametro.objects.all()
    serializer_class = serializers.OutroParametroSerializer


class ParteViewSet(ModelViewSet):
    queryset = models.Parte.objects.all()
    serializer_class = serializers.ParteSerializer


class PrioridadeViewSet(ModelViewSet):
    queryset = models.Prioridade.objects.all()
    serializer_class = serializers.PrioridadeSerializer


class ProcessoPoloDestinatarioViewSet(ModelViewSet):
    queryset = models.ProcessoPoloDestinatario.objects.all()
    serializer_class = serializers.ProcessoPoloDestinatarioSerializer


class ProcessoViewSet(ModelViewSet):
    queryset = models.Processo.objects.all()
    serializer_class = serializers.ProcessoSerializer
    filter_class = filters.ProcessoFilter


class DocumentoTipoViewSet(ModelViewSet):
    queryset = models.DocumentoTipo.objects.all()
    serializer_class = serializers.DocumentoTipoSerializer


class FaseTipoViewSet(ModelViewSet):
    queryset = models.FaseTipo.objects.all()
    serializer_class = serializers.FaseTipoSerializer
