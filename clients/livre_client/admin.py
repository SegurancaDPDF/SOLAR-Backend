# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.contrib import admin

# Solar
from core.admin import AuditoriaVersionAdmin

# Modulos locais
from . import models


# registro do modelo 'HistoricoConsulta' no admin do Django para exibição e gerenciamento no painel de administração
@admin.register(models.HistoricoConsulta)
class HistoricoConsultaAdmin(AuditoriaVersionAdmin):
    list_display = (
        'servico',
        'ip',
        'cadastrado_por',
        'cadastrado_em',
        'sucesso'
    )
    readonly_fields = ('servico', 'parametros', 'ip', 'sucesso', 'resposta')
    search_fields = ('servico', 'cadastrado_por')
