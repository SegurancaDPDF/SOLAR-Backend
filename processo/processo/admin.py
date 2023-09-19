# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.contrib import admin

# Bibliotecas de terceiros
from reversion.admin import VersionAdmin

# Solar
from core.admin import AuditoriaVersionAdmin

# Modulos locais
from . import models


class AcaoAdmin(VersionAdmin):
    search_fields = ('nome', 'codigo_eproc', 'codigo_cnj')
    list_display = ('nome', 'area', 'codigo_cnj', 'extrajudicial', 'ativo')
    list_filter = ('judicial', 'extrajudicial', 'ativo', 'area')


class AssuntoAdmin(VersionAdmin):
    search_fields = ('nome', 'codigo_eproc', 'codigo_cnj')
    list_display = ('nome', 'codigo_eproc', 'codigo_cnj', 'ativo')
    list_filter = ('ativo',)


class AudienciaAdmin(VersionAdmin):
    readonly_fields = (
        'processo', 'parte', 'tipo', 'defensor_cadastro', 'defensor_substituto', 'data_protocolo', 'usuario_eproc',
        'evento_eproc', 'atividade', 'plantao', 'automatico', 'data_cadastro', 'cadastrado_por', 'data_exclusao',
        'excluido_por', 'data_baixa', 'baixado_por')
    search_fields = ('processo__numero', 'tipo__nome')
    list_display = (
        'processo',
        'tipo',
        'audiencia_status',
        'automatico',
        'plantao',
        'evento_eproc',
        'usuario_eproc',
        'data_cad',
        'ativo')
    list_filter = ('audiencia_status',)

    def data_cad(self, obj):
        return obj.data_cadastro.strftime("%d/%m/%Y - %H:%M")


class DocumentoFaseAdmin(VersionAdmin):
    readonly_fields = ('fase', 'eproc', 'nome', 'arquivo', 'data_enviado', 'enviado_por', 'ativo', 'documento_atendimento')
    search_fields = ('nome', 'fase__tipo__nome', 'fase__processo__numero')
    list_display = ('fase', 'nome', 'data_enviado', 'ativo')


class DocumentoTipoAdmin(VersionAdmin):
    search_fields = ('nome', 'eproc')
    list_display = ('nome', 'grau', 'eproc', 'recurso', 'ativo')
    list_filter = ('grau', 'recurso', 'ativo')


class FaseAdmin(VersionAdmin):
    readonly_fields = (
        'processo', 'parte', 'tipo', 'defensor_cadastro', 'defensor_substituto', 'usuario_eproc', 'evento_eproc',
        'atividade', 'plantao', 'automatico', 'data_cadastro', 'cadastrado_por', 'modificado_em',
        'modificado_por', 'data_exclusao', 'excluido_por')
    search_fields = ('tipo__nome', 'processo__numero')
    list_display = (
        'processo',
        'tipo',
        'automatico',
        'plantao',
        'evento_eproc',
        'usuario_eproc',
        'data_cad',
        'data_prot',
        'ativo'
    )
    list_filter = ('automatico', 'ativo')

    @admin.display(ordering='data_cadastro', description='Data Cadastro')
    def data_cad(self, obj):
        return obj.data_cadastro.strftime("%d/%m/%Y - %H:%M")

    @admin.display(ordering='data_protocolo', description='Data Protocolo')
    def data_prot(self, obj):
        if obj.data_protocolo is not None:
            return obj.data_protocolo.strftime("%d/%m/%Y - %H:%M")


class FaseTipoAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome', 'nome_norm', 'codigo_cnj', 'codigo_eproc')
    list_display = ('nome', 'codigo_cnj', 'codigo_eproc', 'peticao_inicial', 'habeas_corpus', 'audiencia', 'juri', 'sentenca', 'recurso', 'judicial',
                    'extrajudicial', '_ativo')
    list_filter = ('judicial', 'extrajudicial', 'peticao_inicial', 'habeas_corpus', 'audiencia', 'juri', 'sentenca', 'recurso')
    readonly_fields = ('nome_norm', )


class ManifestacaoAdmin(AuditoriaVersionAdmin):
    search_fields = ('id', 'parte__processo__numero', 'parte__processo__numero_puro')
    list_display = ('id', 'parte', 'tipo', 'situacao', 'enviando', 'enviado', '_ativo')
    list_filter = ('tipo', 'situacao', 'sistema_webservice', 'enviado')
    readonly_fields = ('parte', 'fase')


class ManifestacaoAvisoAdmin(AuditoriaVersionAdmin):
    list_display = ('id', 'manifestacao', 'numero', '_ativo')


class ManifestacaoDocumentoAdmin(AuditoriaVersionAdmin):
    list_display = ('id', 'manifestacao', 'origem', 'tipo_mni', 'nivel_sigilo', '_ativo')


class OutroParametroAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome', 'tipo', '_ativo')


class ParteAdmin(VersionAdmin):
    readonly_fields = (
        'processo',
        'atendimento',
        'data_cadastro',
        'cadastrado_por',
        'modificado_em',
        'modificado_por',
        'data_exclusao',
        'excluido_por',
        'defensor',
        'defensor_cadastro',
        'defensoria',
        'defensoria_cadastro'
    )
    search_fields = ('processo__numero', 'processo__numero_puro', 'atendimento__numero')
    list_display = ('processo', 'parte', 'atendimento', 'atendimento_ativo', 'defensor_cadastro', 'ativo')
    list_filter = (
        'processo__tipo',
        'parte',
        'processo__pre_cadastro',
        'atendimento__defensoria__nucleo',
        'atendimento__defensoria__comarca'
    )

    def atendimento_ativo(self, obj):
        if obj.atendimento:
            return "At.(%s) - Ativo" % (
                obj.atendimento.get_tipo_display()) if obj.atendimento.ativo else "At.(%s) - Desativado" % (
                obj.atendimento.get_tipo_display())


class ParteHistoricoTransferenciaAdmin(VersionAdmin):
    readonly_fields = (
        'parte',
        'atendimento_antigo',
        'atendimento_novo',
        'cadastrado_em',
        'cadastrado_por',
        'modificado_em',
        'modificado_por',
        'desativado_em',
        'desativado_por'
    )
    search_fields = (
        'parte__processo__numero',
        'parte__processo__numero_puro',
        'atendimento_antigo__numero',
        'atendimento_novo__numero'
    )
    list_display = ('parte', 'atendimento_antigo', 'atendimento_novo', 'cadastrado_em', 'cadastrado_por')


class PrioridadeAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome', 'codigo_mni')
    list_filter = ('disponivel_para_peticionamento',)
    list_display = ('nome', 'codigo_mni', 'disponivel_para_peticionamento', 'cadastrado_em', 'cadastrado_por')


class ProcessoAdmin(VersionAdmin):
    readonly_fields = (
        'numero_puro',
        'situacao',
        'originario',
        'peticao_inicial',
        'assuntos',
        'prioridades',
        'data_cadastro',
        'cadastrado_por',
        'modificado_em',
        'modificado_por',
        'data_exclusao',
        'excluido_por'
    )
    search_fields = ('numero', 'numero_puro', 'chave')
    list_display = (
        'numero',
        'numero_puro',
        'credencial_mni_cadastro',
        'chave',
        'data_cadastro',
        'acao',
        'tipo',
        'comarca',
        'grau',
        'pre_cadastro',
        'ativo'
    )
    list_filter = ('grau', 'tipo', 'ativo', 'pre_cadastro', 'comarca__nome')

    def data_cad(self, obj):
        return obj.data_cadastro.strftime("%d/%m/%Y - %H:%M")


class ParteHistoricoSituacaoAdmin (AuditoriaVersionAdmin):
    readonly_fields = AuditoriaVersionAdmin.readonly_fields + (
        'parte', 'status', 'motivo', 'inicio_sobrestamento', 'fim_sobrestamento'
    )
    search_fields = (
        'parte__processo__numero',
        'parte__processo__numero_puro',
    )
    list_display = ('parte', 'status', 'cadastrado_em', 'cadastrado_por')


@admin.register(models.ProcessoDashboard)
class ProcessoDashboardAdmin(admin.ModelAdmin):
    change_list_template = 'admin_customizado/processo_dashboard.html'

    # date_hierarchy = 'termino_consulta'
    class Media:
        css = {
            # "all": ("my_styles.css",)
        }

        js = (
            "js/admin_customizado/processos_pendentes.js",
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super(ProcessoDashboardAdmin, self).changelist_view(
            request,
            extra_context=extra_context,
        )

        return response


class ProcessoPoloDestinatarioAdmin(AuditoriaVersionAdmin):
    pass


admin.site.register(models.Acao, AcaoAdmin)
admin.site.register(models.Assunto, AssuntoAdmin)
admin.site.register(models.Audiencia, AudienciaAdmin)
admin.site.register(models.DocumentoFase, DocumentoFaseAdmin)
admin.site.register(models.DocumentoTipo, DocumentoTipoAdmin)
admin.site.register(models.Fase, FaseAdmin)
admin.site.register(models.FaseTipo, FaseTipoAdmin)
admin.site.register(models.Manifestacao, ManifestacaoAdmin)
admin.site.register(models.ManifestacaoAviso, ManifestacaoAvisoAdmin)
admin.site.register(models.OutroParametro, OutroParametroAdmin)
admin.site.register(models.ManifestacaoDocumento, ManifestacaoDocumentoAdmin)
admin.site.register(models.Parte, ParteAdmin)
admin.site.register(models.ParteHistoricoTransferencia, ParteHistoricoTransferenciaAdmin)
admin.site.register(models.Prioridade, PrioridadeAdmin)
admin.site.register(models.Processo, ProcessoAdmin)
admin.site.register(models.ProcessoApenso)
admin.site.register(models.ProcessoPoloDestinatario, ProcessoPoloDestinatarioAdmin)
admin.site.register(models.ParteHistoricoSituacao, ParteHistoricoSituacaoAdmin)
