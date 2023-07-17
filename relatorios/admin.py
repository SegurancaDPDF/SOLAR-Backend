# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.contrib import admin

# Solar
from core.admin import AuditoriaVersionAdmin

# Modulos locais
from . import models


class LocalAdmin(AuditoriaVersionAdmin):
    readonly_fields = (
        'cadastrado_por',
        'cadastrado_em',
        'modificado_por',
        'modificado_em',
        'desativado_por',
        'desativado_em',
    ) # campos somente leitura exibidos na página de administracao

    list_filter = (
        'relatorios',
    ) # filtros disponiveis para a lista de locais

    list_display = (
        'titulo',
        'pagina',
        'posicao',
        '_ativo'
    ) # campos exibidos na lista de locais

    search_fields = (
        'pagina',
        'titulo',
    ) # campos pesquisaveis na l


class RelatorioAdmin(AuditoriaVersionAdmin):
    readonly_fields = (
        'cadastrado_por',
        'cadastrado_em',
        'modificado_por',
        'modificado_em',
        'desativado_por',
        'desativado_em',
    )

    list_display = (
        'titulo',
        'caminho',
        'parametros',
        '_ativo'
    )

    search_fields = (
        'titulo',
        'caminho',
    )


admin.site.register(models.Local, LocalAdmin)
admin.site.register(models.Relatorio, RelatorioAdmin)
