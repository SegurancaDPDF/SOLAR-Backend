# -*- coding: utf-8 -*-

# Bibliotecas de terceiros
from django.db.models import Manager

# Bibliotecas Solar
from core.managers import AuditoriaBaseQuerySet


class LocalQuerySet(AuditoriaBaseQuerySet):
    def nao_parametrizaveis(self):
        from .models import Local
        return self.exclude(pagina=Local.PAGINA_RELATORIO_LISTAR)

    def parametrizaveis(self):
        from .models import Local
        return self.filter(pagina=Local.PAGINA_RELATORIO_LISTAR)


class LocalManager(Manager.from_queryset(LocalQuerySet)):
    pass
