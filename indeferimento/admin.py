# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.contrib import admin
from . import models


class IndeferimentoAdmin(admin.ModelAdmin):
    # campos somente leitura na interface administrativa
    readonly_fields = (
        'processo',
        'atendimento',
        'pessoa',
        'defensor',
        'defensoria'
    )
    # Campos exibidos na lista de registros
    list_display = (
        'processo',
        'core_processo_numero',
        'atendimento',
        'pessoa',
        'resultado',
        'tipo_baixa',
        'defensor',
        'defensoria'
    )
    # campos utilizados para pesquisa
    search_fields = (
        'atendimento__numero',
        'processo__numero',
        'processo__uuid'
    )
    # filtros disponíveis na interface administrativa
    list_filter = (
        'resultado',
        'tipo_baixa',
        'processo__situacao'
    )

    # função personalizada para exibir o número do processo
    def core_processo_numero(self, obj):
        if obj.processo:
            # return obj.documento_online.pk
            return obj.processo.numero
        else:
            return None

    core_processo_numero.short_description = "NÚMERO"


admin.site.register(models.Indeferimento, IndeferimentoAdmin)
