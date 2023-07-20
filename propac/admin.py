from django.contrib import admin

from reversion.admin import VersionAdmin

from . import models


# classe para personalizar a exibição do modelo Procedimento no Django Admin
class ProcedimentoAdmin(VersionAdmin):
    readonly_fields = (
        'uuid', 'data_ultima_movimentacao', 'cadastrado_por', 'defensor_responsavel', 'defensoria_responsavel',
        'atendimentos', 'defensorias_acesso')
    list_display = ('numero', 'tipo', 'data_ultima_movimentacao', 'situacao', 'ativo', 'uuid')
    search_fields = ('numero', 'uuid', 'assunto')
    list_filter = ('tipo', 'situacao', 'ativo')


# personalizar a exibição do modelo DocumentoPropac no Django Admin.
class DocumentoPropacAdmin(admin.ModelAdmin):
    list_display = (
        'documento',
        'anexo_original_nome_arquivo',
        'tipo_anexo',
        'movimento',
    )


# personalizar a exibição do modelo TipoAnexoDocumentoPropac no Django Admin
class TipoAnexoDocumentoPropacAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
    )


# definir como o modelo DocumentoPropac será apresentado como inline em MovimentoAdmin
class DocumentoPropacInline(admin.TabularInline):
    model = models.DocumentoPropac
    extra = 0


# personalizar a exibição do modelo Movimento no Django Admin
class MovimentoAdmin(VersionAdmin):
    readonly_fields = (
        # 'procedimento',
        'cadastrado_por',
        'eh_precadastro',
        # 'tipo'
    )
    list_display = (
        'pk', 'procedimento', 'volume', 'ordem_volume', 'data_cadastro', 'data_remocao', 'eh_precadastro', 'ativo')
    search_fields = ('procedimento__numero', 'procedimento__uuid', 'procedimento__assunto')
    list_filter = ('ativo',)
    inlines = [DocumentoPropacInline, ]


# personalizar a exibição do modelo SituacaoProcedimento no Django Admin
class SituacaoProcedimentoAdmin(VersionAdmin):
    readonly_fields = ('procedimento', 'cadastrado_por')
    list_display = ('procedimento', 'situacao', 'data_cadastro', 'ativo')
    search_fields = ('procedimento__numero', 'procedimento__uuid', 'procedimento__assunto')
    list_filter = ('situacao', 'ativo')


# personalizar a exibição do modelo MovimentoTipo no Django Admin
class MovimentoTipoAdmin(VersionAdmin):
    list_display = ('nome', 'codigo', 'instauracao', 'ativo')
    search_fields = ('nome', 'codigo')
    list_filter = ('instauracao', 'ativo')


admin.site.register(models.TipoAnexoDocumentoPropac, TipoAnexoDocumentoPropacAdmin)
admin.site.register(models.DocumentoPropac, DocumentoPropacAdmin)
admin.site.register(models.Procedimento, ProcedimentoAdmin)
admin.site.register(models.Movimento, MovimentoAdmin)
admin.site.register(models.MovimentoTipo, MovimentoTipoAdmin)
admin.site.register(models.SituacaoProcedimento, SituacaoProcedimentoAdmin)
