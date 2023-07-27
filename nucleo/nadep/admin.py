# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from reversion.admin import VersionAdmin
from django.contrib import admin

# Modulos Solar
from core.admin import AuditoriaAdmin, AuditoriaVersionAdmin

# Modulos locais
from .models import (
    EstabelecimentoPenal,
    Prisao,
    Tipificacao,
    TipoEstabelecimentoPenal,
    Falta,
    Aprisionamento,
    Remissao,
    Interrupcao,
    PenaRestritiva,
    RestricaoPrestacaoServico,
    MudancaRegime,
    Soltura,
    Historico,
    CalculoExecucaoPenal,
    MotivoBaixaPrisao,
)


class PrisaoAdmin(VersionAdmin):  # define as colunas a serem exibidas na lista de exibição do modelo Prisao
    list_display = ('pessoa', 'processo', 'tipificacao', 'tipo', 'fracao_pr', 'fracao_lc', 'reicidente', 'ativo')
    list_filter = ('ativo', 'reicidente', 'tipo')
    readonly_fields = (
        'pessoa',
        'processo',
        'parte',
        'origem',
        'data_cadastro',
        'cadastrado_por',
        'data_baixa',
        'motivo_baixa',
        'baixado_por',
        'data_exclusao',
        'excluido_por'
    )
    # define os campos de pesquisa na lista de exibição do modelo Prisao
    search_fields = ('pessoa__nome', 'estabelecimento_penal__nome', 'tipificacao__nome',)


class EstabelecimentoPenalAdmin(VersionAdmin):
    # define configurações para a administração do modelo EstabelecimentoPenal
    list_display = ('nome', 'tipo', 'destinado_ao_sexo', 'inspecionado_pela_dpe', 'ativo')
    list_filter = ('ativo', 'tipo', 'destinado_ao_sexo', 'inspecionado_pela_dpe')
    readonly_fields = ('endereco', 'telefone')
    search_fields = ('nome', 'endereco__municipio__nome')


class TipificacaoAdmin(AuditoriaVersionAdmin):
    # define configurações para a administração do modelo Tipificacao
    list_display = ('nome', 'numero_lei', 'artigo_lei', 'paragrafo_lei', '_ativo',)
    list_filter = ('tipo', 'numero_lei',)
    search_fields = ('nome',)


class TipoEstabelecimentoPenalAdmin(AuditoriaVersionAdmin):
    # define configurações para a administração do modelo TipoEstabelecimentoPenal
    list_display = ('nome', '_ativo',)
    search_fields = ('nome',)


class FaltaAdmin(VersionAdmin):
    # define configurações para a administração do modelo Falta
    list_display = ('pessoa', 'data_fato', 'numero_pad', 'observacao', 'resultado', 'ativo')
    list_filter = ('ativo', 'resultado',)
    readonly_fields = ('pessoa', 'data_cadastro', 'cadastrado_por', 'data_exclusao', 'excluido_por')
    search_fields = ('pessoa', 'numero_pad')


class AprisionamentoAdmin(VersionAdmin):
    # define configurações para a administração do modelo Aprisionamento
    list_display = (
        'nome_preso',
        'numero_processo',
        'estabelecimento_penal',
        'data_inicial',
        'data_final',
        'situacao',
        'detracao',
        'ativo',
    )
    list_filter = ('ativo', 'situacao', 'detracao', 'estabelecimento_penal',)
    readonly_fields = (
        'prisao',
        'estabelecimento_penal',
        'data_inicial',
        'data_final',
        'historico',
        'situacao',
        'origem_cadastro',
        'data_cadastro',
        'cadastrado_por',
        'data_exclusao',
        'excluido_por',
        'ativo'
    )
    search_fields = ('prisao__pessoa__nome', 'historico')

    def nome_preso(self, obj):
        return obj.prisao.pessoa.nome

    def numero_processo(self, obj):
        if obj.prisao.processo:
            return obj.prisao.processo.numero


class RemissaoAdmin(VersionAdmin):
    # define configurações para a administração do modelo Remissao
    list_display = (
        'pessoa',
        'data_inicial',
        'data_final',
        'tipo',
        'dias_registro',
        'dias_remissao',
        'para_progressao',
        'ativo'
    )
    list_filter = ('ativo', 'tipo', 'para_progressao')
    readonly_fields = ('pessoa', 'data_cadastro', 'cadastrado_por')
    search_fields = ('pessoa__nome',)


class InterrupcaoAdmin(VersionAdmin):
    # define configurações para a administração do modelo Interrupcao.
    list_display = ('pessoa', 'data_inicial', 'data_final', 'observacao', 'ativo',)
    list_filter = ('ativo',)
    readonly_fields = ('pessoa', 'data_cadastro', 'cadastrado_por')
    search_fields = ('pessoa__nome', 'observacao',)


class PenaRestritivaAdmin(VersionAdmin):
    # define configurações para a administração do modelo PenaRestritiva.
    list_display = ('prisao', 'restricao', 'ativo',)
    list_filter = ('restricao', 'ativo',)
    readonly_fields = ('prisao', 'data_cadastro', 'cadastrado_por', 'data_exclusao', 'excluido_por')
    search_fields = ('prisao__pessoa__nome', 'prisao__processo__numero_puro')


class RestricaoPrestacaoServicoAdmin(VersionAdmin):
    # define configurações para a administração do modelo RestricaoPrestacaoServico.
    list_display = ('prisao', 'data_referencia', 'horas', 'ativo',)
    list_filter = ('ativo',)
    readonly_fields = ('prisao', 'data_cadastro', 'cadastrado_por', 'data_exclusao', 'excluido_por')
    search_fields = ('prisao__pessoa__nome', 'prisao__processo__numero_puro')

    def horas(self, obj):
        if obj.horas_trabalhadas:
            minutos, segundos = divmod(obj.horas_trabalhadas.seconds, 60)
            horas, minutos = divmod(minutos, 60)
            horas += (obj.horas_trabalhadas.days * 24)
            return '{0}:{1:02d}:{2:02d}'.format(horas, minutos, segundos)


class MudancaRegimeAdmin(VersionAdmin):
    # define configurações para a administração do modelo MudancaRegime.
    list_display = ('prisao', 'tipo', 'regime', 'data_registro', 'data_base', 'estabelecimento_penal', 'ativo',)
    list_filter = ('ativo',)
    readonly_fields = ('prisao', 'data_cadastro', 'cadastrado_por', 'data_exclusao', 'excluido_por')
    search_fields = ('prisao__pessoa__nome', 'prisao__processo__numero_puro')


class SolturaAdmin(VersionAdmin):
    # define configurações para a administração do modelo Soltura.
    list_display = ('aprisionamento', 'data_registro', 'processo', 'tipo', 'ativo')
    list_select_related = ('aprisionamento', 'processo')
    list_filter = ('ativo',)
    readonly_fields = (
        'aprisionamento',
        'processo',
        'data_cadastro',
        'cadastrado_por',
        'data_exclusao',
        'excluido_por'
    )
    search_fields = ('aprisionamento__prisao__pessoa__nome', 'processo__numero_puro')

    def data_registro(self, obj):
        return obj.aprisionamento.data_final


class HistoricoAdmin(VersionAdmin):
    # define configurações para a administração do modelo Historico
    list_display = ('pessoa', 'data_registro', 'evento', 'ativo')
    list_filter = ('ativo', 'evento')
    readonly_fields = ('pessoa', 'data_cadastro', 'cadastrado_por', 'data_exclusao', 'excluido_por')
    search_fields = ('pessoa__nome',)


class CalculoExecucaoPenalAdmin(VersionAdmin):
    # define configurações para a administração do modelo CalculoExecucaoPenal.
    list_display = (
        'pessoa_nome',
        'execucao_numero',
        'regime_atual',
        'estabelecimento_penal_nome',
        'data_progressao',
    )
    list_filter = ('ativo', 'regime_atual', 'estabelecimento_penal',)
    readonly_fields = ('pessoa', 'execucao',)
    search_fields = ('pessoa_nome', 'execucao_numero',)


class MotivoBaixaPrisaoAdmin(AuditoriaAdmin):
    # define configurações para a administração do modelo MotivoBaixaPrisao.
    pass


admin.site.register(Prisao, PrisaoAdmin)
admin.site.register(EstabelecimentoPenal, EstabelecimentoPenalAdmin)
admin.site.register(Tipificacao, TipificacaoAdmin)
admin.site.register(TipoEstabelecimentoPenal, TipoEstabelecimentoPenalAdmin)
admin.site.register(Falta, FaltaAdmin)
admin.site.register(Aprisionamento, AprisionamentoAdmin)
admin.site.register(Remissao, RemissaoAdmin)
admin.site.register(Interrupcao, InterrupcaoAdmin)
admin.site.register(PenaRestritiva, PenaRestritivaAdmin)
admin.site.register(RestricaoPrestacaoServico, RestricaoPrestacaoServicoAdmin)
admin.site.register(MudancaRegime, MudancaRegimeAdmin)
admin.site.register(Soltura, SolturaAdmin)
admin.site.register(Historico, HistoricoAdmin)
admin.site.register(CalculoExecucaoPenal, CalculoExecucaoPenalAdmin)
admin.site.register(MotivoBaixaPrisao, MotivoBaixaPrisaoAdmin)
