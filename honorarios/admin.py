# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from reversion.admin import VersionAdmin
from django.contrib import admin

# Modulos locais
from .models import (
    Honorario,
    Movimento,
    Analise,
    Documento,
    AlertaProcessoMovimento
)


class HonorarioAdmin(VersionAdmin):
    # permite configurar a exibição e edição dos registros de Honorario no painel de administração do Django
    readonly_fields = (
        'recurso_vinculado',
        'data_cadastro',
        'cadastrado_por',
        'modificado_em',
        'modificado_por',
        'fase',
        'honorario_origem',
        'atendimento',
        'defensor',
        'defensoria',
        'excluido_por',
        'data_exclusao'
    )
    search_fields = ('fase__processo__numero', 'fase__processo__numero_puro', 'id')
    list_display = ('dados_honorario', 'situacao', 'data_cadastro', 'excluido', 'possivel', 'ativo')
    list_filter = ('situacao', 'possivel',)

    def dados_honorario(self, obj):
        return 'Honorário ID:{0} | Processo Número: {1} '.format(obj.id, obj.fase.processo.numero)

    def excluido(self, obj):
        if obj.data_exclusao:
            return obj.data_exclusao.strftime("%d/%m/%y %H:%M:%S")
        else:
            return ''


class MovimentoAdmin(VersionAdmin):
    # permite configurar a exibição e edição dos registros de Movimento no painel de administração do Django
    list_display = ('honorario', 'id', 'tipo', 'data_cadastro', 'ativo')
    readonly_fields = ('honorario', 'defensoria', 'excluido_por', 'data_exclusao')
    list_filter = ('ativo',)


class AnaliseAdmin(VersionAdmin):
    # permite configurar a exibição e edição dos registros de Analise no painel de administração do Django
    list_display = ('processo_analise', 'Distribuido_Possivel_ou_nao', 'data_cadastro', 'motivo_Pendencia', 'ativo')
    readonly_fields = ('data_cadastro', 'cadastrado_por', 'fase')
    search_fields = ('fase__processo__numero', 'fase__tipo__nome', 'fase__id')
    list_filter = ('ativo',)

    def motivo_Pendencia(self, obj):
        return '{0}'.format(obj.motivo[:50]+'...' if obj.motivo else '')

    def processo_analise(self, obj):
        return '{0}'.format(obj.fase.processo.numero)

    def Distribuido_Possivel_ou_nao(self, obj):
        if obj.fase.honorario:
            if obj.fase.honorario.possivel:
                return 'Possível'
            else:
                return 'Impossivel'


class DocumentoMovimentoAdmin(VersionAdmin):
    # permite configurar a exibição e edição dos registros de Documento no painel de administração do Django
    list_display = ('movimento_id', 'nome', 'visivel', 'ativo')
    readonly_fields = ('movimento',)
    search_fields = ('nome', 'movimento__honorario__fase__processo__numero')


class AlertaProcessoMovimentoAdmin(VersionAdmin):
    # permite configurar a exibicao e edição dos registros de AlertaProcessoMovimento no painel de administração
    readonly_fields = ('honorario', 'visualizado_por', 'visualizado_por_nome')
    list_display = ('data_cadastro', 'honorario', 'visualizado', 'ativo')


admin.site.register(Honorario, HonorarioAdmin)
admin.site.register(Movimento, MovimentoAdmin)
admin.site.register(Analise, AnaliseAdmin)
admin.site.register(Documento, DocumentoMovimentoAdmin)
admin.site.register(AlertaProcessoMovimento, AlertaProcessoMovimentoAdmin)
