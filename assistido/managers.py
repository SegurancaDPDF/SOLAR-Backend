# -*- coding: utf-8 -*-

# Bibliotecas de terceiros
from django.db.models import QuerySet, Manager

# Solar
from core.managers import AuditoriaBaseQuerySet

# Local
from . import models


# define um conjunto de consultas personalizadas para o modelo Documento
class DocumentoQuerySet(QuerySet):
    def inativos(self):
        return self.filter(ativo=False)  # retorna apenas os documentos marcados como inativos

    def ativos(self):
        return self.filter(ativo=True)  # retorna apenas os documentos marcados como ativos


# define um gerenciador personalizado para o modelo Documento
class DocumentoManager(Manager):
    _queryset_class = DocumentoQuerySet  # especifíca o conjunto de consultas personalizadas a ser usado

    def get_queryset(self):
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints

        return self._queryset_class(**kwargs)  # retorna uma instância do conjunto de consultas personalizadas

    def inativos(self):
        return self.get_queryset().inativos()  # retorna apenas os documentos inativos

    def ativos(self):
        return self.get_queryset().ativos()  # retorna apenas os documentos ativos


# define um conjunto de consultas personalizadas para o modelo Filiacao
class FiliacaoQuerySet(QuerySet):
    def maes(self):
        return self.filter(tipo=models.Filiacao.TIPO_MAE)  # retorna apenas as filiações do tipo mãe

    def pais(self):
        return self.filter(tipo=models.Filiacao.TIPO_PAI)  # retorna apenas as filiações do tipo pai


class FiliacaoManager(Manager.from_queryset(FiliacaoQuerySet)):
    pass


class SituacaoQuerySet(AuditoriaBaseQuerySet):
    pass


class SituacaoManager(Manager.from_queryset(SituacaoQuerySet)):
    pass


class TipoRendaQuerySet(AuditoriaBaseQuerySet):
    pass


class TipoRendaManager(Manager.from_queryset(TipoRendaQuerySet)):
    pass
