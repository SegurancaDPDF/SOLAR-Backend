# third-party
from django_filters import FilterSet, CharFilter

# application
from . import models


class PredioFilter(FilterSet):
    nome = CharFilter(field_name='nome', lookup_expr='icontains')

    class Meta:
        model = models.Predio
        fields = ('nome', 'comarca', 'ativo')
