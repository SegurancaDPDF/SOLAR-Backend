# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from reversion.admin import VersionAdmin
from django.contrib import admin

# Solar
from core.admin import AuditoriaVersionAdmin

# Modulos locais
from .models import Agenda, Evento, Categoria


# utilizada para personalizar a interface administrativa do modelo Evento
class EventoAdmin(VersionAdmin):
    search_fields = (
        'titulo',
        'comarca__nome',
        'defensor__servidor__nome',
    )
    list_display = (
        'titulo',
        'comarca',
        'tipo',
        'defensor',
        'defensoria',
        'periodo',
        'data_validade',
        'ativo',
    )
    list_filter = (
        'tipo',
        'comarca'
    )
    exclude = (
        'tipo',
    )
    readonly_fields = (
        'pai',
        'comarca',
        'defensoria',
        'defensor',
        'cadastrado_por',
        'data_cadastro',
        'autorizado_por',
        'data_autorizacao',
        'excluido_por',
        'data_exclusao'
    )

    def data_cadastro(self, obj):
        return obj.data_cadastro.strftime("%d/%m/%Y %H:%M")

    def principal(self, obj):
        return 'Filho' if obj.pai else 'Pai'

    def periodo(self, obj):
        if obj.data_fim is None:
            return obj.data_ini.strftime("%d/%m/%Y") + ' | --- '
        else:
            return obj.data_ini.strftime("%d/%m/%Y") + ' | ' + obj.data_fim.strftime("%d/%m/%Y")


# utilizada para personalizar a interface administrativa do modelo Agenda
class AgendaAdmin(VersionAdmin):
    search_fields = (
        'titulo',
        'atuacao__defensoria__nome',
        'atuacao__defensor__servidor__nome',
    )
    list_display = (
        'titulo',
        'principal',
        'atuacao',
        'periodo',
        'ativo'
    )
    list_filter = (
        'comarca',
        'defensor'
    )
    exclude = (
        'tipo',
        'defensor',
    )
    readonly_fields = (
        'pai',
        'comarca',
        'defensoria',
        'defensor',
        'atuacao',
        'cadastrado_por',
        'data_cadastro',
        'excluido_por',
        'data_exclusao'
    )

    def data_cadastro(self, obj):
        return obj.data_cadastro.strftime("%d/%m/%Y %H:%M")

    def principal(self, obj):
        return 'Filho' if obj.pai else 'Pai'

    def periodo(self, obj):
        if obj.data_fim is None:
            return obj.data_ini.strftime("%d/%m/%Y") + ' |  ------------- '
        else:
            return obj.data_ini.strftime("%d/%m/%Y") + ' | ' + obj.data_fim.strftime("%d/%m/%Y")


# utilizada para personalizar a interface administrativa do modelo Categoria
class CategoriaAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome',)
    list_display = ('nome', 'sigla')


admin.site.register(Evento, EventoAdmin)
admin.site.register(Agenda, AgendaAdmin)
admin.site.register(Categoria, CategoriaAdmin)
