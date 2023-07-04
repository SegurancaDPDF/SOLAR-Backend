# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from cacheops import invalidate_model
from django.contrib import admin
from django.db import transaction
from django.utils import timezone
from reversion.admin import VersionAdmin

# Modulos locais
from . import models


def desativar(modeladmin, request, queryset):
    # funcao de acao para desativar registros selecionados no admin
    with transaction.atomic():
        queryset.update(
            desativado_por=request.user,
            desativado_em=timezone.now()
        )

    invalidate_model(queryset.model)


desativar.short_description = "Desativa selecionados"


def reativar(modeladmin, request, queryset):
    # funcao de acao para reativar registros selecionados no admin
    with transaction.atomic():
        queryset.update(
            modificado_por=request.user,
            modificado_em=timezone.now(),
            desativado_por=None,
            desativado_em=None
        )

    invalidate_model(queryset.model)


reativar.short_description = "Reativa selecionados"


class AuditoriaAdmin(admin.ModelAdmin):  # classe base para os modelos do admin que possuem campos de auditoria
    actions = [desativar, reativar]

    def __init__(self, model, admin_site):

        super().__init__(model, admin_site)

        if not self.readonly_fields:
            self.readonly_fields = tuple()

        self.readonly_fields = self.readonly_fields + (
            'cadastrado_por',
            'cadastrado_em',
            'modificado_por',
            'modificado_em',
            'desativado_por',
            'desativado_em',
        )


class AuditoriaVersionAdmin(VersionAdmin):   
    # classe base para os modelos do admin que possuem campos de auditoria e histórico de versoes
    actions = [desativar, reativar]
   
    def __init__(self, model, admin_site):

        super().__init__(model, admin_site)

        if not self.readonly_fields:
            self.readonly_fields = tuple()

        self.readonly_fields = self.readonly_fields + (
            'cadastrado_por',
            'cadastrado_em',
            'modificado_por',
            'modificado_em',
            'desativado_por',
            'desativado_em',
        )


class ClasseAdmin(AuditoriaAdmin):  # configuracao do admin do modelo classe
    list_filter = (
        'tipo',
        'tipo_processo'
    )
    list_display = (
        'nome',
        'tipo',
        'tipo_processo',
    )


class ProcessoAdmin(AuditoriaAdmin):  # configuracao do modelo processo
    search_fields = (
        'uuid',
        'numero',
    )
    list_filter = (
        'tipo',
        'situacao'
    )
    list_display = (
        'uuid',
        'numero',
        'setor_criacao',
        'setor_atual',
        'classe',
        'tipo',
        'situacao',
    )
    readonly_fields = AuditoriaAdmin.readonly_fields + (
        'setores_notificados',
    )


class ParteAdmin(AuditoriaAdmin):
    pass


class EventoAdmin(AuditoriaAdmin):  # configuracao do modelo evento
    readonly_fields = AuditoriaAdmin.readonly_fields + (
        'processo',
        'parte',
        'participantes',
        'em_edicao',
    )
    search_fields = (
        'processo__uuid',
        'processo__numero',
    )
    list_filter = (
        'tipo__tipo',
    )
    list_display = (
        'processo',
        'numero',
        'tipo',
        'data_referencia',
        'setor_criacao',
        '_ativo'
    )


class DocumentoAdmin(AuditoriaAdmin):  # configuracao do modelo documento
    search_fields = (
        'processo__uuid',
        'processo__numero',
    )

    readonly_fields = (
        'processo',
        'evento',
        'parte',
        'tipo',
        'modelo',
        'documento',
        'arquivo',
        'nome',
    ) + AuditoriaAdmin.readonly_fields

    list_display = (
        'processo',
        'evento',
        'tipo',
        'nome',
        '_ativo',
    )


class ModeloDocumentoAdmin(AuditoriaAdmin):  # configuracao do modelo modelodocumento
    readonly_fields = AuditoriaAdmin.readonly_fields + (
        'ged_modelo',
    )
    search_fields = (
        'nome',
    )
    list_display = (
        'nome',
        'tipo',
        'ativo'
    )
    list_filter = (
        'tipo',
    )


class TipoDocumentoAdmin(AuditoriaAdmin):  # configuracao modelo tipodocumento
    pass


class TipoEventoAdmin(AuditoriaAdmin):  # configuracao do modelo tipoevento
    readonly_fields = AuditoriaAdmin.readonly_fields + (
        'nome_norm',
    )
    list_display = (
        'nome',
        'tipo',
        'tipo_processo',
        '_ativo',
    )
    list_filter = (
        'tipo',
        'tipo_processo',
    )


admin.site.register(models.Classe, ClasseAdmin)
admin.site.register(models.Processo, ProcessoAdmin)
admin.site.register(models.Parte, ParteAdmin)
admin.site.register(models.Evento, EventoAdmin)
admin.site.register(models.Documento, DocumentoAdmin)
admin.site.register(models.ModeloDocumento, ModeloDocumentoAdmin)
admin.site.register(models.TipoDocumento, TipoDocumentoAdmin)
admin.site.register(models.TipoEvento, TipoEventoAdmin)
