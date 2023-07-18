# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.contrib import admin

# Solar
from core.admin import AuditoriaAdmin, AuditoriaVersionAdmin

# Modulos locais
from . import models

# Classe responsável pela administração do modelo HistoricoConsultaProcessos no painel de administração do Django.
# que herda funcionalidades da classe AuditoriaAdmin


@admin.register(models.HistoricoConsultaProcessos)
class HistoricoConsultaProcessosAdmin(admin.ModelAdmin):
    list_display = (
        'data_inicial',
        'data_final',
        'paginas',
        'registros',
        'sucesso'
    )

# Classe responsável pela administração do modelo HistoricoConsultaDocumento no painel de administração do Django.


@admin.register(models.HistoricoConsultaDocumento)
class HistoricoConsultaDocumentoAdmin(AuditoriaAdmin):
    list_display = (
        'documento',
        'processo',
        'grau',
        'ip',
        'cadastrado_por',
        'cadastrado_em',
        'sucesso'
    )
    readonly_fields = ('processo', 'grau', 'documento', 'sucesso')
    search_fields = ('processo', 'documento')

# Classe responsável pela administração do modelo HistoricoConsultaProcesso no painel de administração do Django.


@admin.register(models.HistoricoConsultaProcesso)
class HistoricoConsultaProcessoAdmin(AuditoriaAdmin):
    list_display = (
        'processo',
        'grau',
        'ip',
        'cadastrado_por',
        'cadastrado_em',
        'sucesso'
    )
    readonly_fields = ('processo', 'grau', 'ip', 'sucesso')
    search_fields = ('processo', 'ip')

# Classe responsável pela administração do modelo HistoricoConsultaAvisos no painel de administração do Django.


@admin.register(models.HistoricoConsultaAvisos)
class HistoricoConsultaAvisosAdmin(AuditoriaAdmin):
    list_display = ('data_consulta',)

# Classe responsável pela administração do modelo HistoricoConsultaTeorComunicacao no painel de administração do Django.


@admin.register(models.HistoricoConsultaTeorComunicacao)
class HistoricoConsultaTeorComunicacaoAdmin(AuditoriaAdmin):
    list_display = (
        'processo',
        'aviso',
        'ip',
        'cadastrado_por',
        'cadastrado_em',
    )
    readonly_fields = ('processo', 'ip')
    search_fields = ('processo', 'ip')

# Classe responsável pela administração do modelo SistemaWebService no painel de administração do Django.


@admin.register(models.SistemaWebService)
class SistemaWebServiceAdmin(AuditoriaVersionAdmin):
    list_display = ('nome', '_ativo')
    search_fields = ('nome',)

# Classe responsável pela administração do modelo Competencia no painel de administração do Django.


@admin.register(models.Competencia)
class CompetenciaAdmin(AuditoriaVersionAdmin):
    list_display = ('nome', 'codigo_mni', 'sistema_webservice', 'area', 'principal', '_ativo')
    search_fields = ('nome', 'codigo_mni')
    list_filter = ('principal', 'sistema_webservice', 'area')

# Classe responsável pela administração do modelo OrgaoJulgador no painel de administração do Django.


@admin.register(models.OrgaoJulgador)
class OrgaoJulgadorAdmin(AuditoriaVersionAdmin):
    list_display = ('nome', 'codigo_mni', 'sistema_webservice', 'vara', '_ativo')
    search_fields = ('nome', 'codigo_mni')
    list_filter = ('sistema_webservice', )

# Classe responsável pela administração do modelo TipoArquivo no painel de administração do Django.


@admin.register(models.TipoArquivo)
class TipoArquivoAdmin(AuditoriaVersionAdmin):
    list_display = ('extensao', 'tamanho_maximo', 'sistema_webservice', '_ativo')
    list_filter = ('sistema_webservice',)
    search_fields = ('extensao',)

# Classe responsável pela administração do modelo TipoEvento no painel de administração do Django.


@admin.register(models.TipoEvento)
class TipoEventoAdmin(AuditoriaVersionAdmin):
    list_display = ('nome', 'codigo_mni', 'sistema_webservice', '_ativo')
    list_filter = ('sistema_webservice', 'disponivel_em_peticao_avulsa', 'disponivel_em_peticao_com_aviso')
    readonly_fields = ('nome_norm', 'tipos_de_fase',)
    search_fields = ('nome', 'codigo_mni')

# Classe responsável pela administração do modelo RespostaTecnica no painel de administração do Django.


@admin.register(models.RespostaTecnica)
class RespostaTecnicaAdmin(AuditoriaVersionAdmin):
    list_display = ('descricao', 'regex', 'resposta_amigavel',)
    search_fields = ('descricao',)

# Classe responsável pela administração do modelo RespostaAmigavel no painel de administração do Django.


@admin.register(models.RespostaAmigavel)
class RespostaAmigavelAdmin(AuditoriaVersionAdmin):
    list_display = ('descricao',)
    search_fields = ('descricao',)
