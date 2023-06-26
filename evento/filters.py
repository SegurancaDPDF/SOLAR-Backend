
# third-party
from django_filters import FilterSet, BooleanFilter, ModelChoiceFilter

# django
from django.db.models import Q

# project
from defensor.models import Defensor

# application
from . import models


# utilizada para filtrar os objetos do modelo Agenda
class AgendaFilter(FilterSet):
    class Meta:
        model = models.Agenda
        fields = ('defensor',)


# utilizada para filtrar os objetos do modelo Evento
class EventoFilter(FilterSet):
    defensor = ModelChoiceFilter(method='get_defensor', label="Defensor", queryset=Defensor.objects.ativos())
    eh_pai = BooleanFilter(field_name='pai', lookup_expr='isnull')

    class Meta:
        model = models.Evento
        fields = ('tipo', 'eh_pai',)

    # utilizado como método de filtragem para o filtro 'defensor'
    def get_defensor(self, queryset, name, value):
        comarcas = set(value.all_atuacoes.ativos().comarcas())

        return queryset.filter(
            (
                Q(defensor=value) |
                Q(comarca__in=comarcas) |
                Q(filhos__comarca__in=comarcas)
            )
        ).distinct()
