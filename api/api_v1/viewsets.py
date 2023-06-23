# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class ListRetrieveModelViewSet(mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               GenericViewSet):
    """
    Um viewset que fornece as ações padrão `retrieve()` and `list()`.
    """
    pass


class ListCreateRetrieveModelViewSet(mixins.CreateModelMixin,
                                     mixins.RetrieveModelMixin,
                                     mixins.ListModelMixin,
                                     GenericViewSet):
    """
    Um viewset que fornece as ações padrão `create()`, `retrieve()` and `list()`.
    """
    pass


class RetrieveCreateModelViewSet(mixins.CreateModelMixin,
                                 mixins.RetrieveModelMixin,
                                 GenericViewSet):
    """
    Um viewset que fornece as ações padrão `create() e `retrieve()`
    """
    pass
