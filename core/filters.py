# third-party
from django_filters import FilterSet

# application
from . import models


class TipoEventoFilter(FilterSet):
    class Meta:
        model = models.TipoEvento
        fields = ('tipo', 'tipo_processo')
