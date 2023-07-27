# -*- coding: utf-8 -*-

# Bibliotecas de terceiros
from django.db.models import QuerySet, Manager


class BaseQuerySet(QuerySet):
    def inativos(self):
        return self.filter(ativo=False)

    def ativos(self):
        return self.filter(ativo=True)


class BaseManager(Manager.from_queryset(BaseQuerySet)):
    pass


class AprisionamentoQuerySet(BaseQuerySet):
    def em_andamento(self):
        return self.filter(data_final=None)


class AprisionamentoManager(Manager.from_queryset(AprisionamentoQuerySet)):
    pass
