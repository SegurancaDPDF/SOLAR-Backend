# third-party
from django_filters import BooleanFilter, CharFilter, DateTimeFilter, FilterSet, ModelChoiceFilter

# application
from . import models

# project
from defensor.models import Defensor


class ManifestacaoFilter(FilterSet):
    # filtrar por data inicial de cadastramento
    data_inicial = DateTimeFilter(field_name='cadastrado_em', lookup_expr='gte')

    # filtrar por data final de cadastramento
    data_final = DateTimeFilter(field_name='cadastrado_em', lookup_expr='lte')

    # filtrar por manifestações ativas ou inativas
    ativo = BooleanFilter(field_name='desativado_em', lookup_expr='isnull')

    class Meta:
        model = models.Manifestacao
        fields = ('data_inicial', 'data_final', 'cadastrado_por', 'defensoria', 'situacao', 'ativo')


class ProcessoFilter(FilterSet):
    # filtrar por defensor associado ao processo
    defensor = ModelChoiceFilter(method='get_defensor', label="Defensor", queryset=Defensor.objects.ativos())

    # filtrar por nome da defensoria associada ao processo
    defensoria = CharFilter(method='get_defensoria', label="Defensoria")

    class Meta:
        model = models.Processo
        fields = ('defensor', 'defensoria', 'ativo')

    def get_defensor(self, queryset, name, value):
        pass

    def get_defensoria(self, queryset, name, value):
        pass


class AudienciaFilter(FilterSet):
    # filtrar por data inicial da audiência
    data_inicial = DateTimeFilter(field_name='data_protocolo', lookup_expr='gte')

    # filtrar por data final da audiência
    data_final = DateTimeFilter(field_name='data_protocolo', lookup_expr='lte')

    # filtrar audiências pelo número do processo associado
    processo = CharFilter('processo__numero_puro', lookup_expr='icontains')

    class Meta:
        model = models.Audiencia
        fields = ('data_inicial', 'data_final', 'defensor_cadastro', 'defensoria', 'processo', 'ativo')
