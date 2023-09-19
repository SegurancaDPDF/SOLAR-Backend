# django
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# third-party
from drf_yasg.utils import swagger_auto_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet

# project
from core.serializers import GenericIdNomeSerializer

# application
from . import filters, models, serializers


class ProcessoApensoViewSet(ModelViewSet):
    queryset = models.ProcessoApenso.objects.all()
    serializer_class = serializers.ProcessoApensoSerializer


class AcaoViewSet(ModelViewSet):
    queryset = models.Acao.objects.all()
    serializer_class = serializers.AcaoSerializer
    filter_class = filters.AcaoFilter


class AssuntoViewSet(ModelViewSet):
    queryset = models.Assunto.objects.all()
    serializer_class = serializers.AssuntoSerializer


class AudienciaViewSet(ModelViewSet):
    queryset = models.Audiencia.objects.all()
    serializer_class = serializers.AudienciaSerializer
    filter_class = filters.AudienciaFilter


class AudienciaTotalViewSet(ListModelMixin, GenericViewSet):
    queryset = models.Audiencia.objects.filter(
        ativo=True,
        processo__ativo=True,
        processo__parte__ativo=True
    ).all()

    serializer_class = serializers.AudienciaTotalSerializer
    filter_class = filters.AudienciaTotalFilter
    permission_classes = [DjangoModelPermissions]

    def list(self, request, *args, **kwargs):
        queryset_data = self.filter_queryset(self.get_queryset())
        serialier = self.get_serializer(data=queryset_data, many=True)
        serialier.is_valid()
        return Response(serialier.data)


class ManifestacaoAvisoViewSet(ModelViewSet):
    queryset = models.ManifestacaoAviso.objects.all()
    serializer_class = serializers.ManifestacaoAvisoSerializer


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
    queryset = models.Processo.objects.all().distinct().order_by('numero_puro')
    serializer_class = serializers.ProcessoSerializer
    filter_class = filters.ProcessoFilter


class PeticaoTotalMensalViewSet(ListModelMixin, GenericViewSet):
    queryset = models.Parte.objects.all()
    serializer_class = serializers.PeticaoTotalMensalSerializar
    filter_class = filters.PeticaoTotalMensalFilter
    permission_classes = [DjangoModelPermissions]

    def list(self, request, *args, **kwargs):
        queryset_data = self.filter_queryset(self.get_queryset())
        serialier = self.get_serializer(data=queryset_data, many=True)
        serialier.is_valid()
        return Response(serialier.data)


class DocumentoTipoViewSet(ModelViewSet):
    queryset = models.DocumentoTipo.objects.all()
    serializer_class = serializers.DocumentoTipoSerializer


class FaseTipoViewSet(ModelViewSet):
    queryset = models.FaseTipo.objects.all()
    serializer_class = serializers.FaseTipoSerializer


class ParteTipoViewSet(ViewSet):
    """Retorna uma lista dos tipos de parte"""

    @method_decorator(cache_page(60 * 60 * 2))  # cache 2 horas
    @swagger_auto_schema(responses={200: GenericIdNomeSerializer(many=True)})
    def list(self, request):
        lista = [{'id': item[0], 'nome': item[1]} for item in models.Parte.LISTA_TIPO]
        serializer = GenericIdNomeSerializer(lista, many=True)
        return Response(serializer.data)


class GrauViewSet(ViewSet):
    LISTA_GRAU = [
        {'id': 1, 'nome': '1º Grau'},
        {'id': 2, 'nome': '2º Grau'},
        {'id': 3, 'nome': 'STF/STJ'},
    ]

    def list(self, request):
        return Response(self.LISTA_GRAU)

    def retrieve(self, request, pk=None):
        grau = next((item for item in self.LISTA_GRAU if item['id'] == int(pk)), None)
        if grau:
            return Response(grau)
        return Response(status=404)
