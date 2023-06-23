# third-party
from rest_framework import mixins
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from django.http import HttpResponse
from http import HTTPStatus
# django
from django.db.models import F, Prefetch, Q

# application
from . import filters
from . import models
from . import serializers


# define as configs para as classes de vizualizacao AtuacaoViewSetV1 e AtuacaoViewSetV2
class AtuacaoViewSetMixin:
    queryset = models.Atuacao.objects.select_related(
        'defensoria',
        'defensor__servidor',
        'titular__servidor',
        'cargo',
        'documento',
        'cadastrado_por__usuario',
        'excluido_por__usuario',
    ).all().order_by(
        'defensor__servidor__nome',
        'data_inicial'
    ).filter(
        Q(data_final__gt=F('data_inicial')) |
        Q(data_final=None)
    )
    serializer_class = serializers.AtuacaoSerializer
    permission_classes = [DjangoModelPermissions]


# classes de visualizacao
class AtuacaoViewSetV1(AtuacaoViewSetMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    filter_class = filters.AtuacaoFilterV1


class AtuacaoViewSetV2(AtuacaoViewSetMixin, ModelViewSet):
    filter_class = filters.AtuacaoFilterV2
    
    def get_serializer_class(self):
        if self.action in ["create"]:
            return serializers.AtuacaoCreateSerializer
        return serializers.AtuacaoSerializer
    
    def destroy(self, request, *args, **kwargs):
        from cacheops import invalidate_model
        try:
            atuacao = models.Atuacao.objects.filter(pk=kwargs['pk'])
            atuacao.update(ativo=False)
            result_http = HttpResponse(atuacao)
            invalidate_model(models.Atuacao)
            return result_http
        except:
            return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        
# manipula objetos Defensor
class DefensorViewSet(ModelViewSet):
    queryset = models.Defensor.objects.filter(
        eh_defensor=True
    ).select_related(
        'servidor__usuario',
    ).prefetch_related(
        Prefetch(
            'all_atuacoes',
            queryset=models.Atuacao.objects.select_related(
                'defensoria',
                'titular__servidor',
                'documento'
            ).vigentes(
                ajustar_horario=False
            )
        )
    )

    serializer_class = serializers.DefensorSerializer
    filter_class = filters.DefensorFilter
    permission_classes = [DjangoModelPermissions]


# manipula objetos Documento. define a propriedade queryset para recuperar todos os documentos.
class DocumentoViewSet(ModelViewSet):
    queryset = models.Documento.objects.all()
    serializer_class = serializers.DocumentoSerializer


# manipula objetos EditalConcorrenciaPlantao. define a propriedade queryset para recuperar todos os editais
class EditalConcorrenciaPlantaoViewSet(ModelViewSet):
    queryset = models.EditalConcorrenciaPlantao.objects.all()
    serializer_class = serializers.EditalConcorrenciaPlantaoSerializer


# manipula objetos VagaEditalPlantao. define a propriedade queryset para recuperar todas as vagas de editais
class VagaEditalPlantaoViewSet(ModelViewSet):
    queryset = models.VagaEditalPlantao.objects.all()
    serializer_class = serializers.VagaEditalPlantaoSerializer
