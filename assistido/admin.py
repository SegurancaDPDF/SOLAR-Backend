# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf import settings
from reversion.admin import VersionAdmin
from django.contrib import admin

# Solar
from core.admin import AuditoriaVersionAdmin

# Modulos locais
from .models import (
    Documento,
    EstruturaMoradia,
    Filiacao,
    Imovel,
    Movel,
    Patrimonio,
    PessoaAssistida,
    Profissao,
    Renda,
    Semovente,
    Situacao,
    PerfilCamposObrigatorios,
    Patrimonial,
    PatrimonialTipo,
    Dependente,
    TipoRenda
)


# configuração personalizada para o admin do modelo PessoaAssistida
class PessoaAssistidaAdmin(AuditoriaVersionAdmin):
    # campos excluídos se a configuração USAR_EDEFENSOR estiver desativada nas configurações do Django
    pre_exclude = []
    if not settings.USAR_EDEFENSOR:
        pre_exclude.append('aderiu_edefensor')
    exclude = pre_exclude
    # campos somente leitura no admin
    readonly_fields = ('tipo_cadastro', 'profissao', 'moradia', 'telefones', 'enderecos', 'deficiencias', 'bens', 'nome_soundex', 'nome_norm')  # noqa: E501
    search_fields = ('apelido', 'nome', 'cpf', 'rg_numero')
    list_display = ('nome', 'data_nascimento', 'cpf', 'rg_numero', '_ativo')


# configuração personalizada para o admin do modelo Filiacao
class FiliacaoAdmin(VersionAdmin):
    readonly_fields = ('pessoa_assistida', 'nome_soundex', 'nome_norm')
    search_fields = ('nome', 'pessoa_assistida__nome')
    list_display = ('nome', 'pessoa_assistida')


class ProfissaoAdmin(VersionAdmin):
    pass


# configuração personalizada para o admin do modelo Documento
class DocumentoAdmin(VersionAdmin):
    readonly_fields = ('pessoa', 'data_enviado', 'enviado_por', 'data_exclusao', 'excluido_por')
    search_fields = ('nome', 'pessoa__nome',)
    list_display = ('pessoa', 'nome', 'ativo')


class RendaAdmin(VersionAdmin):
    pass


class PatrimonioAdmin(VersionAdmin):
    pass


class PatrimonialAdmin(VersionAdmin):
    list_display = ['pessoa', 'tipo']


class PatrimonialTipoAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome',)
    list_filter = ('grupo',)
    list_display = ['nome', 'grupo', '_ativo']


class ImovelAdmin(VersionAdmin):
    pass


class MovelAdmin(VersionAdmin):
    pass


class SemoventeAdmin(VersionAdmin):
    pass


class PerfilCamposObrigatoriosAdmin(VersionAdmin):
    search_fields = ('nome',)
    list_display = ('nome', 'tipo_pessoa', 'tipo_processo', 'tipo_parte', 'parte_principal')
    readonly_fields = ('configuracao',)


class SituacaoAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome',)
    list_display = ('nome', '_ativo')

    def has_delete_permission(self, request, obj=None):
        result = obj.pode_remover if obj else False

        return result

    def get_readonly_fields(self, request, obj=None):
        result = self.readonly_fields

        if obj and not obj.pode_remover:
            result = list(self.readonly_fields) + ["codigo"]

        return result


class EstruturaMoradiaAdmin(VersionAdmin):
    pass


class DependenteAdmin(VersionAdmin):
    search_fields = ('nome',)
    list_display = ('nome', 'situacao', 'parentesco', 'pessoa')


class TipoRendaAdmin(AuditoriaVersionAdmin):
    search_fields = ('nome',)
    list_display = ('nome', 'valor_maximo_deducao', 'eh_deducao_salario_minimo')


admin.site.register(Documento, DocumentoAdmin)
admin.site.register(EstruturaMoradia, EstruturaMoradiaAdmin)
admin.site.register(Filiacao, FiliacaoAdmin)
admin.site.register(Imovel, ImovelAdmin)
admin.site.register(Movel, MovelAdmin)
admin.site.register(Patrimonio, PatrimonioAdmin)
admin.site.register(PerfilCamposObrigatorios, PerfilCamposObrigatoriosAdmin)
admin.site.register(PessoaAssistida, PessoaAssistidaAdmin)
admin.site.register(Profissao, ProfissaoAdmin)
admin.site.register(Renda, RendaAdmin)
admin.site.register(Semovente, SemoventeAdmin)
admin.site.register(Situacao, SituacaoAdmin)
admin.site.register(Patrimonial, PatrimonialAdmin)
admin.site.register(PatrimonialTipo, PatrimonialTipoAdmin)
admin.site.register(Dependente, DependenteAdmin)
admin.site.register(TipoRenda, TipoRendaAdmin)
