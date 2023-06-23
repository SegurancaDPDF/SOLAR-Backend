from django.db.models import Q
from django_filters import FilterSet, BooleanFilter, ModelChoiceFilter, CharFilter, DateTimeFilter

from contrib.models import Servidor

from . import models


# define filtros para a classe Atuacao do model.
class AtuacaoFilter(FilterSet):
    data_inicial = DateTimeFilter(field_name='data_inicial', lookup_expr='lte', label='Data Inicial')
    data_final = DateTimeFilter(method='get_data_final', label='Data Final')

    def get_data_final(self, queryset, name, value):
        return queryset.filter(
            Q(data_final__gte=value) |
            Q(data_final=None)
        )

    def get_defensoria(self, queryset, name, value):
        from contrib.models import Defensoria

        defensorias_ids = value.split(',')

        if self.form.cleaned_data.get('incluir_defensorias_filhas') or self.form.cleaned_data.get('incluir_filhos'):
            defensorias_filhas = Defensoria.objects.filter(mae__in=defensorias_ids).values_list('id', flat=True)
            defensorias_ids += list(defensorias_filhas)

        return queryset.filter(defensoria__in=defensorias_ids)

    def get_incluir_filhos(self, queryset, name, value):
        return queryset

    def get_esta_vigente(self, queryset, name, value):
        return queryset.vigentes()


# filtros adicionais
class AtuacaoFilterV1(AtuacaoFilter):
    servidor_id = ModelChoiceFilter(field_name='defensor', label="Servidor", queryset=models.Defensor.objects.ativos())
    defensoria_id = CharFilter(method='get_defensoria', label="Defensoria")
    apenas_defensor = BooleanFilter(field_name='defensor__eh_defensor', label='É defensor?')
    apenas_vigentes = BooleanFilter(method='get_esta_vigente', label='Está vigente?')
    incluir_defensorias_filhas = BooleanFilter(method='get_incluir_filhos', label='Incluir atuações de defensorias filhas?')

    class Meta:
        model = models.Atuacao
        fields = ('tipo', 'servidor_id', 'defensoria_id', 'data_inicial', 'data_final', 'apenas_defensor',
                  'apenas_vigentes', 'incluir_defensorias_filhas', 'ativo',)

    def get_apenas_defensor(self, queryset, name, value):
        return queryset.nao_lotacoes().filter(defensor__eh_defensor=True)


class AtuacaoFilterV2(AtuacaoFilter):
    servidor = ModelChoiceFilter(field_name='defensor__servidor', label="Servidor", queryset=Servidor.objects.all())
    defensoria = CharFilter(method='get_defensoria', label="Defensoria")
    eh_defensor = BooleanFilter(field_name='defensor__eh_defensor', label='É defensor?')
    esta_vigente = BooleanFilter(method='get_esta_vigente', label='Está vigente?')
    incluir_filhos = BooleanFilter(method='get_incluir_filhos', label='Incluir atuações de defensorias filhas?')

    class Meta:
        model = models.Atuacao
        fields = ('tipo', 'defensor', 'servidor', 'defensoria', 'data_inicial', 'data_final', 'eh_defensor',
                  'esta_vigente', 'incluir_filhos', 'ativo',)


# filtros para a classe Defensor do model
class DefensorFilter(FilterSet):
    incluir_atuacoes = BooleanFilter(method='get_incluir_atuacoes', label='Incluir atuações vigentes?')

    class Meta:
        model = models.Defensor
        fields = ('servidor', 'incluir_atuacoes', 'ativo')

    def get_incluir_atuacoes(self, queryset, name, value):
        return queryset
