# -*- coding: utf-8 -*-

# Bibliotecas de terceiros
from django.db.models import Manager

# Bibliotecas Solar
from core.managers import AuditoriaBaseQuerySet


class LocalQuerySet(AuditoriaBaseQuerySet):
    # Retorna os Locais que não são parametrizáveis, excluindo aqueles com a página igual a PAGINA_RELATORIO_LISTAR
    def nao_parametrizaveis(self):
        from .models import Local
        return self.exclude(pagina=Local.PAGINA_RELATORIO_LISTAR)

    def parametrizaveis(self):
        # # Retorna os Locais que são parametrizáveis, filtrando aqueles com a página igual a PAGINA_RELATORIO_LISTAR
        from .models import Local
        return self.filter(pagina=Local.PAGINA_RELATORIO_LISTAR)


class LocalManager(Manager.from_queryset(LocalQuerySet)):
    pass
