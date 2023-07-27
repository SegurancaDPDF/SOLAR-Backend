# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from reversion.admin import VersionAdmin
from django.contrib import admin

# Modulos locais
from .models import Guiche, Predio


class GuicheAdmin(VersionAdmin):
    search_fields = ('comarca__nome', 'predio__nome', 'numero')
    list_display = ('comarca', 'predio', 'numero',)
    list_filter = ('predio', 'comarca',)


class PredioAdmin(VersionAdmin):
    search_fields = ('comarca__nome', 'nome',)
    readonly_fields = ('endereco', 'telefone',)
    list_display = ('comarca', 'nome', 'endereco', 'visao_comarca', 'ativo')
    list_filter = ('comarca',)


admin.site.register(Guiche, GuicheAdmin)
admin.site.register(Predio, PredioAdmin)
