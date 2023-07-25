# third-party
from rest_framework import filters


class DistribuirAvisosFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        sistema = request.query_params.get('sistema')
        defensor = request.query_params.get('defensor')

        if sistema:
            queryset = [obj for obj in queryset if obj.get('sistema') == sistema]

        if defensor:
            queryset = [obj for obj in queryset if obj.get('defensor') == defensor]

        return queryset
