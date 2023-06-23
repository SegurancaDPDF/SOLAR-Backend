# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from rest_framework.pagination import PageNumberPagination


# define a paginação padrão para os resultados
#  pode ser alterado através do parâmetro page_size_query_param
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def paginate_queryset(self, queryset, request, view=None):
        # q = queryset.only('pk')
        return super(StandardResultsSetPagination, self).paginate_queryset(queryset, request, view)


# define uma paginacão especifica para o resultado
# o tamanho da página é definido como 100
class AtendimentoResultsSetPagination(StandardResultsSetPagination):
    page_size = 100


# define uma paginação especial onde apenas um item é exibido por página
class OnlyOnePerPagePaginator(StandardResultsSetPagination):
    page_size = 1
    max_page_size = 1
