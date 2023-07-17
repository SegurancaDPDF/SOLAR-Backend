# third-party
from django_filters import FilterSet, BooleanFilter, CharFilter

# application
from . import models


class RelatorioFilter(FilterSet):
    titulo = CharFilter(field_name='titulo', lookup_expr='icontains')
    ativo = BooleanFilter(field_name='desativado_em', lookup_expr='isnull')

    class Meta:
        model = models.Relatorio
        fields = ('titulo', 'tipo', 'locais', 'papeis', 'ativo')
