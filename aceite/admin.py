# -*- coding: utf-8 -*-
# Importações necessárias

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.contrib import admin

from reversion.admin import VersionAdmin
from core.admin import AuditoriaAdmin
from .models import Termo, TermoResposta

# Função para atribuir valores


@admin.register(Termo)
class TermoAdmin(AuditoriaAdmin, VersionAdmin):
    search_fields = ('titulo', 'descricao')
    list_display = ('titulo', 'data_inicio', 'data_finalizacao', '_ativo')
    ordering = ['-data_inicio']

# Função para desativar um objetos


def soft_delete(request, obj):
    obj.desativar(request.user)

# Função para registrar o TermoResposta no painel de administração do Django


@admin.register(TermoResposta)
class RespostaAdmin(AuditoriaAdmin, VersionAdmin):
    search_fields = ('termo__titulo', 'servidor__nome')
    list_display = ('termo', 'servidor', 'aceite', 'data_resposta')
    readonly_fields = (
        'termo',
        'servidor',
        'aceite',
        'titulo_termo',
        'descricao_termo',
        'data_resposta',
        'desativado_em',
        'desativado_por'
    )
    ordering = ['-data_resposta']
    actions = ['action_delete']

    # Chamando a função de desativar o objeto

    def get_actions(self, request):
        actions = super(RespostaAdmin, self).get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_model(self, request, obj):
        soft_delete(request, obj)

    def action_delete(self, request, obj):
        for resp in obj:
            soft_delete(request, resp)

    action_delete.short_description = 'Remover respostas dos termos'
