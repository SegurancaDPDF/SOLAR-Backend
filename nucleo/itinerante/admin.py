# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from reversion.admin import VersionAdmin
from django.contrib import admin

# Modulos locais
from .models import Evento


# utilizada para personalizar a exibição do modelo Evento no painel de administração do Django
class EventoAdmin(VersionAdmin):
    search_fields = (
        'titulo',
        'municipio__nome',
        'defensoria__nome',
        'participantes__usuario__first_name',
        'participantes__usuario__last_name'
    )
    list_display = (
        'titulo',
        'data_inicial',
        'data_final',
        'municipio',
        'defensoria',
        'ativo'
    )
    list_filter = (
        'defensoria__nome',
        'ativo'
    )
    readonly_fields = (
        'municipio',
        'defensoria',
        'participantes',
        'atuacoes',
        'data_cadastro',
        'cadastrado_por',
        'data_autorizacao',
        'autorizado_por',
        'excluido_por',
        'data_exclusao'
    )


admin.site.register(Evento, EventoAdmin)
