# -*- coding: utf-8 -*-
# Importações necessárias

from core.models import Processo as CoreProcesso
from core.managers import EventoManager, EventoQuerySet, TipoEventoManager, TipoEventoQuerySet

# Herda as funcionalidades de EventoQuerySet


class AtividadeExtraordinariaQuerySet(EventoQuerySet):
    pass

# Esta classe sobrescreve o método get_queryset para filtrar os objetos com base no tipo de processo
# Retorna um objeto AtividadeExtraordinariaQuerySet filtrado


class AtividadeExtraordinariaManager(EventoManager):
    def get_queryset(self):
        return AtividadeExtraordinariaQuerySet(
            model=self.model,
            using=self._db
        ).filter(
            tipo__tipo_processo=CoreProcesso.TIPO_ATIVIDADE
        )

# Herda as funcionalidades de TipoEventoQuerySet


class AtividadeExtraordinariaTipoQuerySet(TipoEventoQuerySet):
    pass

# Retorna um objeto AtividadeExtraordinariaTipoQuerySet filtrado


class AtividadeExtraordinariaTipoManager(TipoEventoManager):
    def get_queryset(self):
        return AtividadeExtraordinariaTipoQuerySet(
            model=self.model,
            using=self._db
        ).filter(
            tipo_processo=CoreProcesso.TIPO_ATIVIDADE
        )
