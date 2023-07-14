# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.conf import settings
from reversion.admin import VersionAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Solar
from core.admin import AuditoriaAdmin, AuditoriaVersionAdmin

from contrib.models import (
    Area,
    Atualizacao,
    Bairro,
    Cargo,
    CEP,
    Comarca,
    Defensoria,
    DefensoriaVara,
    DefensoriaTipoEvento,
    Deficiencia,
    Documento,
    Endereco,
    EnderecoHistorico,
    Estado,
    Etiqueta,
    IdentidadeGenero,
    MenuExtra,
    Municipio,
    OrientacaoSexual,
    Pais,
    Papel,
    Salario,
    Servidor,
    Telefone,
    Vara,
    HistoricoLogin,
    GeneroPessoa
)


class AtualizacaoAdmin(VersionAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    search_fields = ('texto',)
    list_display = ('data', 'tipo', 'texto', 'ativo')
    list_filter = ('tipo',)


class TelefoneAdmin(VersionAdmin):
    pass


class CEPAdmin(AuditoriaVersionAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    search_fields = ('cep',)
    list_display = ('cep', 'estado', 'municipio', 'logradouro', 'bairro', 'eh_geral')
    list_filter = ('eh_geral', 'municipio__estado__uf',)
    readonly_fields = ('bairro', 'logradouro', 'complemento')

    def estado(self, obj):  # exibe o estado relacionado a um objeto CEP
        if obj.municipio:
            return obj.municipio.estado.uf
        else:
            return ''


class EnderecoAdmin(VersionAdmin):  # define campos de pesquisa e exibição em lista para este model
    search_fields = ('logradouro', 'bairro__nome', 'municipio__nome')
    list_display = ('logradouro', 'numero', 'complemento', 'cep', 'bairro', 'municipio')
    readonly_fields = ('bairro', 'municipio', 'desativado_por', 'desativado_em')


class EnderecoHistoricoAdmin(VersionAdmin):  # define campos de pesquisa e exibição em lista para este model
    search_fields = ('logradouro', 'bairro__nome', 'municipio__nome')
    list_display = ('logradouro', 'numero', 'complemento', 'cep', 'bairro', 'municipio')
    readonly_fields = (
        'bairro',
        'municipio',
        'desativado_por',
        'desativado_em',
        'logradouro',
        'numero',
        'complemento',
        'cep'
    )


class PaisAdmin(VersionAdmin):
    pass


class EstadoAdmin(VersionAdmin):
    pass


class MunicipioAdmin(VersionAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    list_display = ('nome', 'estado', 'comarca')
    list_filter = ('estado', 'comarca')


class BairroAdmin(AuditoriaVersionAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    search_fields = ('nome',)
    list_display = ('nome', 'municipio', '_ativo',)
    list_filter = ('municipio__estado__uf',)
    readonly_fields = ('nome_norm',)


class AreaAdmin(VersionAdmin):  # define campos de exibição em lista e filtros para este model
    list_display = ('nome', 'penal', 'ativo')
    list_filter = ('penal', 'ativo')


class ComarcaAdmin(VersionAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    search_fields = ('nome', 'codigo_eproc',)
    list_display = ('nome', 'codigo', 'codigo_eproc', 'coordenadoria_comarca', 'ativo',)
    list_filter = ('ativo', 'coordenadoria',)
    readonly_fields = ('data_cadastro', 'data_atualizacao')

    @staticmethod
    def coordenadoria_comarca(obj):
        if obj.coordenadoria is None:
            return obj.nome
        else:
            return obj.coordenadoria.nome


class DefensoriaAdmin(VersionAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    pre_exclude = ['documentos']
    if not settings.USAR_EDEFENSOR:
        pre_exclude.append('aderiu_chat_edefensor')
    exclude = pre_exclude

    # TODO: Remover esta linha pois provavelmente o sistema pre-exclude já faz isso.
    exclude = ('documentos',)
    search_fields = ('nome', 'numero')
    list_display = ('nome', 'numero', 'comarca', 'atuacao', 'predio', 'ativo')
    list_filter = ('ativo', 'agendamento_online', 'comarca', 'nucleo')


class DefensoriaVaraAdmin(AuditoriaVersionAdmin):  # Define campos de pesquisa, exibição em lista e filtros
    list_display = ('defensoria', 'vara', 'paridade', 'principal', '_ativo')
    search_fields = ('defensoria__nome', 'vara__nome')
    list_filter = ('paridade', 'principal',)


class DefensoriaTipoEventoAdmin(VersionAdmin):  # define campos de pesquisa, exibição em lista e filtros
    list_display = ('defensoria', 'tipo_evento', 'conta_estatistica')
    search_fields = ('defensoria__nome', 'tipo_evento__nome')
    list_filter = ('conta_estatistica',)


class DocumentoAdmin(VersionAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    list_display = ('nome', 'exibir_em_documento_assistido', 'exibir_em_documento_atendimento', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo', 'exibir_em_documento_assistido', 'exibir_em_documento_atendimento')


class DeficienciaAdmin(VersionAdmin):
    pass


class VaraAdmin(VersionAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    search_fields = ('nome', 'codigo_eproc',)
    list_display = ('nome', 'comarca', 'grau', 'codigo_eproc', 'ativo',)
    list_filter = ('ativo', 'grau', 'comarca',)
    readonly_fields = ('data_cadastro', 'data_atualizacao',)


class SalarioAdmin(VersionAdmin):  # define campos de exibição em lista para este model
    list_display = (
        'valor',
        'vigencia',
        'indice_renda_individual',
        'indice_renda_familiar',
        'indice_renda_per_capita',
        'indice_valor_bens',
        'indice_valor_investimentos'
    )


class ServidorInline(admin.StackedInline):
    model = Servidor
    # list_display = ('nome', 'data_atualizacao')
    readonly_fields = ('nome', 'data_atualizacao', 'telefones')


class CustomUserAdmin(UserAdmin):
    inlines = [ServidorInline]
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'servidor__cpf',
        'servidor__matricula',
    )
    list_display = UserAdmin.list_display + (
        'is_active',
        'show_matricula',
        'show_cpf',
        'show_papel'
    )
    list_filter = UserAdmin.list_filter + (
        'servidor__papel',
    )

    # bloqueia alteração de grupos e permissões do usuário (herdadas a partir do papel do usuário)
    readonly_fields = (
        'groups',
        'user_permissions',
    )

    def get_queryset(self, request):
        qs = super(CustomUserAdmin, self).get_queryset(request)
        qs.select_related('servidor__defensor__supervisor')
        return qs

    def show_matricula(self, obj):
        ret = ''
        if obj.servidor:
            ret = obj.servidor.matricula
        return ret

    def show_cpf(self, obj):
        ret = ''
        if obj.servidor:
            ret = obj.servidor.cpf
        return ret

    def show_papel(self, obj):
        ret = ''
        if obj.servidor and obj.servidor.papel:
            ret = obj.servidor.papel.nome
        return ret

    show_papel.short_description = 'Papel'
    show_cpf.short_description = 'CPF'
    show_matricula.short_description = 'Matricula'


class PapelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'marcar_usuario_como_defensor', 'requer_supervisor', 'requer_matricula', 'grupos_display', 'ativo']
    filter_horizontal = ['grupos']

    search_fields = ('nome',)
    list_filter = ('ativo', 'marcar_usuario_como_defensor', 'requer_supervisor', 'requer_matricula')

    def grupos_display(self, obj):
        grupos = obj.grupos.all().order_by('name').values_list('name', flat=True)
        return ', '.join(grupos)

    grupos_display.short_description = 'Grupos de Permissões'
    # grupos_display.admin_order_field = 'grupos'


class CargoAdmin(VersionAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    search_fields = ('nome', 'nome_norm', 'codigo',)
    list_display = ('nome', 'codigo', 'desativado_em')
    readonly_fields = ('cadastrado_em',
                       'modificado_em',
                       'cadastrado_por',
                       'modificado_por',
                       'desativado_por',
                       'desativado_em')


class MenuExtraAdmin(AuditoriaAdmin):  # define campos de pesquisa, exibição em lista e filtros para este model
    search_fields = ('nome', 'descricao')
    list_display = ('nome', 'descricao', 'local', 'posicao', 'url', '_ativo')
    list_filter = ('local',)


class OrientacaoSexualAdmin(AuditoriaVersionAdmin):  # define campos de pesquisa, exibição em lista e filtros
    search_fields = ('nome',)
    list_display = ('nome', '_ativo')


class IdentidadeGeneroAdmin(AuditoriaVersionAdmin):  # define campos de pesquisa, exibição em lista e filtros
    search_fields = ('nome',)
    list_display = ('nome', '_ativo')


class GeneroPessoaAdmin(AuditoriaVersionAdmin):  # define campos de pesquisa, exibição em lista e filtros
    search_fields = ('nome',)
    list_display = ('nome', '_ativo')


@admin.register(HistoricoLogin)
class HistoricoLoginAdmin(AuditoriaVersionAdmin):  # define campos de exibição em lista para este model
    list_display = ('endereco_ip', 'cadastrado_em', 'cadastrado_por', 'info_navegador', 'logout')


@admin.register(Etiqueta)
class EtiquetaAdmin(AuditoriaVersionAdmin):  # define campos de exibição em lista para este model
    list_display = ('nome', '_ativo')


admin.site.register(Area, AreaAdmin)
admin.site.register(Atualizacao, AtualizacaoAdmin)
admin.site.register(Bairro, BairroAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(CEP, CEPAdmin)
admin.site.register(Comarca, ComarcaAdmin)
admin.site.register(Defensoria, DefensoriaAdmin)
admin.site.register(DefensoriaVara, DefensoriaVaraAdmin)
admin.site.register(DefensoriaTipoEvento, DefensoriaTipoEventoAdmin)
admin.site.register(Deficiencia, DeficienciaAdmin)
admin.site.register(Documento, DocumentoAdmin)
admin.site.register(Endereco, EnderecoAdmin)
admin.site.register(EnderecoHistorico, EnderecoHistoricoAdmin)
admin.site.register(Estado, EstadoAdmin)
admin.site.register(IdentidadeGenero, IdentidadeGeneroAdmin)
admin.site.register(MenuExtra, MenuExtraAdmin)
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(OrientacaoSexual, OrientacaoSexualAdmin)
admin.site.register(Pais, PaisAdmin)
admin.site.register(Papel, PapelAdmin)
admin.site.register(Salario, SalarioAdmin)
admin.site.register(Telefone, TelefoneAdmin)
admin.site.register(Vara, VaraAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(GeneroPessoa, GeneroPessoaAdmin)
