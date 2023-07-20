from rest_framework import filters


class MovimentoFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        movimento = request.GET.get('movimento')

        if movimento:
            return queryset.filter(movimento__id=movimento)

        return queryset
