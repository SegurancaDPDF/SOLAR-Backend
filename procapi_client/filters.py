# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import coreapi
from rest_framework.filters import BaseFilterBackend

# Classe responsável por filtrar os resultados com base no "sistema_webservice".


class SistemaWebserviceFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="sistema_webservice",
                          required=False,
                          location='query',
                          type='string',
                          description='Nome do sistema webservice (Ex: EPROC-1G-TO)'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "codigo_competencia".


class CompetenciaWebserviceFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="codigo_competencia",
                          required=False,
                          location='query',
                          type='string',
                          description='Código da competência no Sistema do Tribunal de Justiça'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "codigo_classe".


class ClasseWebserviceFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="codigo_classe",
                          required=False,
                          location='query',
                          type='string',
                          description='Código da classe no Sistema do Tribunal de Justiça'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no código da "comarca".


class ComarcaWebserviceFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="comarca",
                          required=False,
                          location='query',
                          type='string',
                          description='Código da comarca no Sistema do Tribunal de Justiça'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "numero_processo".


class NumeroProcessoFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="numero_processo",
                          required=True,
                          location='query',
                          type='string',
                          description='Número do Processo Para Ser Atualizado'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "cpf_defensor".


class CpfDefensorFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="cpf_defensor",
                          required=False,
                          location='query',
                          type='string',
                          description='Vincula o Cadastro do Processo ao CPF informado'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "processo_numero".


class ProcessoNumeroFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="processo_numero",
                          required=True,
                          location='query',
                          type='string',
                          description='Número do Processo'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "codigo_procapi".


class CodigoProcapiManifestacaoFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="codigo_procapi",
                          required=True,
                          location='query',
                          type='string',
                          description='Id da Manifestação do PROCAPI vinculado ao SOLAR'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "numero_aviso".


class AvisoFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="numero_aviso",
                          required=True,
                          location='query',
                          type='string',
                          description='Numero do Aviso a Ser Distribuido'),
            coreapi.Field(name="codigo_orgao_julgador",
                          required=False,
                          location='query',
                          type='string',
                          description='Código do Orgão Julgador no Qual Processo está vinculado'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no número da "vara".


class VaraFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="vara",
                          required=False,
                          location='query',
                          type='string',
                          description='Numero da vara'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base na "paridade".


class ParidadeFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="paridade",
                          required=False,
                          location='query',
                          type='string',
                          description='Selecionar Paridade'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "defensor".


class DefensorFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="defensor",
                          required=False,
                          location='query',
                          type='string',
                          description='Passar o id do defensor'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base na "defensoria".


class DefensoriaFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="defensoria",
                          required=False,
                          location='query',
                          type='string',
                          description='Passar o id da defensoria'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base na "page".


class PageFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="page",
                          required=False,
                          location='query',
                          type='string',
                          description='Passar o número da página'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "codigo_localidade".


class LocalidadeFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="codigo_localidade",
                          required=False,
                          location='query',
                          type='string',
                          description='Código da Localidade no Sistema do Tribunal de Justiça'),
        ]

        return fields

# Classe responsável por filtrar os resultados com base no "responsavel".


class ResponsavelFilter(BaseFilterBackend):
    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(name="responsavel",
                          required=False,
                          location='query',
                          type='string',
                          description='Passar o id do defensor'),
        ]

        return fields
