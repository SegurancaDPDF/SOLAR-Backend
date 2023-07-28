# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas Padrão
from datetime import datetime

# Bibliotecas de terceiros
from reversion.admin import VersionAdmin
from django.contrib import admin, messages
from django.db import transaction
from django.utils.translation import ngettext

# Solar
from core.admin import AuditoriaVersionAdmin
from .models import (
    Acordo,
    Atendimento,
    Coletivo,
    Defensor,
    Documento,
    Encaminhamento,
    Especializado,
    Impedimento,
    Informacao,
    Justificativa,
    ModeloDocumento,
    Pergunta,
    Pessoa,
    Procedimento,
    Qualificacao,
    QualificacaoAssunto,
    Tarefa,
    Assunto,
    AtendimentoParticipante,
    FormaAtendimento,
    TipoColetividade,
    MotivoExclusao,
    GrupoDeDefensoriasParaAgendamento,
    TipoVulnerabilidade,
    PastaDocumento)


# função de ação para desativar registros selecionados no admin
@admin.action(description='Desativa selecionados')
def desativar(modeladmin, request, queryset):
    # cria uma transação atômica para garantir que todas as operações ocorram ou nenhuma ocorra
    with transaction.atomic():
        total = queryset.update(
            excluido_por=request.user.servidor,
            data_exclusao=datetime.now(),
            ativo=False
        )
        # exibe uma mensagem de sucesso para o usuário após a ação
        modeladmin.message_user(request, ngettext(
            '%d registro foi desativado.',
            '%d registros foram desativados.',
            total,
        ) % total, messages.SUCCESS)


# função de ação para reativar registros selecionados no admin
@admin.action(description='Reativa selecionados')
def reativar(modeladmin, request, queryset):
    # cria uma transação atômica para garantir que todas as operações ocorram ou nenhuma ocorra
    with transaction.atomic():
        total = queryset.update(
            modificado_por=request.user.servidor,
            data_modificacao=datetime.now(),
            excluido_por=None,
            data_exclusao=None,
            ativo=True
        )
        # exibe uma mensagem de sucesso para o usuário após a ação
        modeladmin.message_user(request, ngettext(
            '%d registro foi reativado.',
            '%d registros foram reativados.',
            total,
        ) % total, messages.SUCCESS)


# classe para personalizar a interface de administração do modelo Acordo
class AcordoAdmin(VersionAdmin):
    readonly_fields = ('atendimento', 'termo', 'tipo', 'ativo')


# classe para personalizar a interface de administração do modelo Atendimento
class AtendimentoAdmin(VersionAdmin):
    readonly_fields = ('qualificacao', 'agendado_por', 'atendido_por', 'inicial', 'origem', 'remarcado',
                       'remarcado_auto', 'nucleo', 'prazo', 'prioridade', 'data_cadastro', 'cadastrado_por',
                       'modificado_por', 'data_modificacao',
                       'data_exclusao', 'excluido_por', 'tipo_motivo_exclusao', 'motivo_exclusao', 'ativo', 'assuntos')
    search_fields = ('numero',)
    list_display = ('numero', 'tipo', 'data_agendamento', 'data_atendimento', 'ativo')
    list_filter = ('tipo',)
    actions = [desativar, reativar]

# outras classes personalizadas para a interface de administração dos demais modelos


class AtendimentoParticipanteAdmin(VersionAdmin):
    search_fields = ('atendimento__numero', 'servidor__nome')
    list_filter = ('cargo',)
    list_display = ('atendimento', 'servidor', 'cargo')
    readonly_fields = ('atendimento', 'servidor')


class AtendimentoPessoaAdmin(VersionAdmin):
    search_fields = ('atendimento__numero', 'pessoa__nome')
    list_display = ('atendimento', 'responsavel', 'pessoa', 'tipo', 'ativo')
    readonly_fields = ('atendimento', 'pessoa', 'representante',)


class ColetivoAdmin(VersionAdmin):
    list_display = ('atendimento', 'comunidade', 'propac')


class DefensorAdmin(VersionAdmin):
    readonly_fields = (
        'qualificacao', 'defensoria', 'defensor', 'substituto', 'responsavel', 'agendado_por', 'atendido_por',
        'finalizado_por', 'inicial', 'origem', 'remarcado', 'remarcado_auto', 'nucleo', 'prazo',
        'data_cadastro', 'cadastrado_por', 'modificado_por', 'data_modificacao', 'data_exclusao', 'excluido_por',
        'tipo_motivo_exclusao', 'motivo_exclusao', 'ativo', 'assuntos', 'impedimento', 'comarca'
    )
    search_fields = ('numero',)
    list_display = ('numero', 'tipo', 'defensoria', 'defensor', 'data_agendamento', 'data_atendimento', 'ativo')
    list_filter = ('tipo', 'ativo')
    actions = [desativar, reativar]


class DocumentoAdmin(VersionAdmin):
    readonly_fields = (
        'atendimento',
        'impedimento',
        'pessoa',
        'documento',
        'documento_online',
        'documento_resposta',
        'data_enviado',
        'enviado_por',
        'data_cadastro',
        'cadastrado_por',
        'data_exclusao',
        'excluido_por'
    )
    search_fields = ('atendimento__numero', 'nome', 'documento_online__id')
    list_display = ('atendimento', 'nome', 'documento_online_id_versao', 'enviado_por', 'data_enviado', 'ativo')

    def documento_online_id_versao(self, obj):
        if obj.documento_online:
            # return obj.documento_online.pk
            return obj.documento_online.identificador_versao
        else:
            return None

    documento_online_id_versao.short_description = "GED ID"


class EncaminhamentoAdmin(VersionAdmin):
    readonly_fields = (
        'endereco',
        'telefone',
    )
    search_fields = ('nome',)
    list_display = ('nome', 'ativo')


class EspecializadoAdmin(VersionAdmin):
    pass


class ImpedimentoAdmin(VersionAdmin):
    readonly_fields = ('defensor', 'pessoa', 'atendimento', 'razao', 'data_cadastro', 'cadastrado_por',
                       'anotacao_avaliacao', 'avaliado_por', 'resultado')
    search_fields = ('pessoa__nome', 'defensor__servidor__nome', 'atendimento__numero')
    list_display = ('pessoa', 'defensor', 'atendimento', 'razao', 'resultado', 'ativo')
    list_filter = ('resultado', 'ativo')


class JustificativaAdmin(VersionAdmin):
    pass


class InformacaoAdmin(VersionAdmin):
    search_fields = ('titulo',)
    list_display = ('titulo', 'ativo')


class ModeloDocumentoAdmin(VersionAdmin):
    search_fields = ('nome',)
    list_display = ('nome', 'tipo', 'ativo')
    list_filter = ('tipo', 'ativo')


class QualificacaoAdmin(VersionAdmin):
    search_fields = ('titulo',)
    list_display = ('titulo', 'area', 'nucleo', 'especializado', 'tipo', 'ativo')
    list_filter = ('ativo', 'tipo', 'disponivel_para_agendamento_via_app', 'area', 'nucleo')
    readonly_fields = ('titulo_norm',)


class QualificacaoAssuntoAdmin(AuditoriaVersionAdmin):
    list_display = ('qualificacao', 'assunto', 'principal', '_ativo')
    search_fields = ('qualificacao', 'assunto')
    list_filter = ('principal',)


class PerguntaAdmin(VersionAdmin):
    pass


class ProcedimentoAdmin(VersionAdmin):
    search_fields = ('ligacao__numero',)
    list_display = ('ligacao', 'tipo', 'data_cadastro')
    list_filter = ('tipo',)


class TarefaAdmin(VersionAdmin):
    exclude = ('documentos',)
    readonly_fields = (
        'origem',
        'documento',
        'atendimento',
        'processo',
        'data_finalizado',
        'finalizado',
        'data_cadastro',
        'cadastrado_por',
        'data_exclusao',
        'excluido_por'
    )
    search_fields = (
        'titulo', 'atendimento__numero', 'responsavel__usuario__last_name', 'responsavel__usuario__first_name')
    list_display = ('atendimento_numero', 'tipo', 'tarefa_titulo', 'tarefa_responsavel', 'ativo')
    # list_filter = ('tipo',)

    def tipo(self, obj):
        if obj.origem is None:
            return 'Pedido'
        else:
            return 'Resposta'

    def atendimento_numero(self, obj):
        if obj.origem is None:
            if obj.atendimento:
                return obj.atendimento.numero
            elif obj.movimento.procedimento.atendimentos.first():
                return obj.movimento.procedimento.atendimentos.first()
            else:
                return None
        else:
            return obj.origem.atendimento.numero

    def tarefa_titulo(self, obj):
        if obj.origem is None:
            return obj.titulo
        else:
            return obj.origem.titulo

    def tarefa_responsavel(self, obj):
        if obj.origem is None:
            return obj.responsavel
        else:
            return obj.origem.responsavel


class AssuntoAdmin(VersionAdmin):
    readonly_fields = (
        'titulo',
        'pai',
        'ordem',
        'descricao',
        'ativo',
        'data_cadastro',
        'cadastrado_por',
        'data_exclusao',
        'excluido_por'
    )
    search_fields = ('titulo', 'ordem')
    list_display = ('titulo', 'ordem', 'descricao', 'ativo')
    list_filter = ('ordem', 'ativo')


class FormaAtendimentoAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome',)
    list_display = (
        'nome',
        'data_ini',
        'data_fim',
        'aparece_defensor',
        'aparece_recepcao',
        'conta_estatistica',
        'por_ligacao',
        'por_app_mensagem',
        'por_email',
        'presencial'
    )
    list_filter = (
        'aparece_defensor',
        'aparece_recepcao',
        'conta_estatistica',
        'por_ligacao',
        'por_app_mensagem',
        'por_email',
        'presencial'
    )

    def data_ini(self, obj):
        return obj.data_inicial.strftime("%d/%m/%Y - %H:%M")

    def data_fim(self, obj):
        if obj.data_final:
            return obj.data_final.strftime("%d/%m/%Y - %H:%M")


class TipoColetividadeAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome',)
    list_display = (
        'nome',
        'data_ini',
        'data_fim',
        'conta_estatistica',
        'individual',
        'coletivo',
        'difuso'
    )
    list_filter = (
        'conta_estatistica',
        'individual',
        'coletivo',
        'difuso'
    )

    def data_ini(self, obj):
        return obj.data_inicial.strftime("%d/%m/%Y - %H:%M")

    def data_fim(self, obj):
        if obj.data_final:
            return obj.data_final.strftime("%d/%m/%Y - %H:%M")


class MotivoExclusaoAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome',)


class GrupoDeDefensoriasParaAgendamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'defensorias_display', 'ativo']
    filter_horizontal = ['defensorias', ]

    search_fields = ('nome',)
    list_filter = ('ativo', )

    def defensorias_display(self, obj):
        defensorias = obj.defensorias.all().order_by('nome').values_list('nome', flat=True)
        return ', '.join(defensorias)

    defensorias_display.short_description = 'Grupo de Defensorias Para Agendamento'


class TipoVulnerabilidadeAdmin(AuditoriaVersionAdmin):
    list_display = ['nome', 'descricao', ]
    search_fields = ['nome', ]


class PastaAtendimentoAdmin(AuditoriaVersionAdmin):
    raw_id_fields = ('atendimento',)


# registro dos modelos personalizados no painel de administração
admin.site.register(Acordo, AcordoAdmin)
admin.site.register(Documento, DocumentoAdmin)
admin.site.register(ModeloDocumento, ModeloDocumentoAdmin)
admin.site.register(Encaminhamento, EncaminhamentoAdmin)
admin.site.register(Informacao, InformacaoAdmin)
admin.site.register(Atendimento, AtendimentoAdmin)
admin.site.register(Defensor, DefensorAdmin)
admin.site.register(Coletivo, ColetivoAdmin)
admin.site.register(Qualificacao, QualificacaoAdmin)
admin.site.register(QualificacaoAssunto, QualificacaoAssuntoAdmin)
admin.site.register(Pergunta)
admin.site.register(Pessoa, AtendimentoPessoaAdmin)
admin.site.register(Procedimento, ProcedimentoAdmin)
admin.site.register(Tarefa, TarefaAdmin)
admin.site.register(Especializado, EspecializadoAdmin)
admin.site.register(Impedimento, ImpedimentoAdmin)
admin.site.register(Justificativa, JustificativaAdmin)
admin.site.register(Assunto, AssuntoAdmin)
admin.site.register(AtendimentoParticipante, AtendimentoParticipanteAdmin)
admin.site.register(FormaAtendimento, FormaAtendimentoAdmin)
admin.site.register(TipoColetividade, TipoColetividadeAdmin)
admin.site.register(MotivoExclusao, MotivoExclusaoAdmin)
admin.site.register(GrupoDeDefensoriasParaAgendamento, GrupoDeDefensoriasParaAgendamentoAdmin)
admin.site.register(TipoVulnerabilidade, TipoVulnerabilidadeAdmin)
admin.site.register(PastaDocumento, PastaAtendimentoAdmin)
