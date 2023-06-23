# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import coreapi
from django_filters.rest_framework import DjangoFilterBackend
from assistido.models import PessoaAssistida
from atendimento.atendimento.models import Defensor as AtendimentoDefensor, Documento
from indeferimento.models import Indeferimento
from processo.processo.models import Processo


# define um filtro personalizado para o modelo AtendimentoDefensor
#  especifica os campos pelos quais os registros podem ser filtrados e fornece os campos de esquema 
# correspondentes para documentação da API.
class AtendimentoDefensorFilterBackend(DjangoFilterBackend):
    class Meta:
        model = AtendimentoDefensor
        fields = ('numero', 'partes__pessoa')

    def get_schema_fields(self, view):
        fields = super(AtendimentoDefensorFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(name="numero", required=False, location='query', type='integer'),
            coreapi.Field(name="data_inicial", required=False, location='query', type='string'),
            coreapi.Field(name="data_final", required=False, location='query', type='string'),
            coreapi.Field(name="partes__pessoa", required=False, location='query', type='integer'),
            coreapi.Field(name="defensoria_id", required=False, location='query', type='integer'),
            coreapi.Field(name="soagendamentos",
                          description='mostra só os atendimentos que NÃO possuem data_atendimento',
                          required=False, location='query', type='boolean'),
            coreapi.Field(name="soagendamentosfuturos",
                          description='filtra os atendimentos monstrando somente os de data futura'
                                      ' a data hora de consulta.'
                                      'Só funciona em conjunto com "soagendamentos"',
                          required=False, location='query', type='boolean'),
            coreapi.Field(name="incluirprecadastro",
                          description='inclui atendimentos do tipo ligação (pré-cadastro) na listagem',
                          required=False, location='query', type='boolean'),
            coreapi.Field(name="incluiranotacao",
                          description='inclui atendimentos do tipo anotação na listagem',
                          required=False, location='query', type='boolean'),
            coreapi.Field(name="ativo",
                          description='(opcional) true: apenas registros ativos; false: apenas registros inativos',
                          required=False,
                          location='query',
                          type='boolean'),
        ]

        fields.extend(f)
        return fields


# define um filtro personalizado para o modelo Documento
# adiciona um campo de filtro para exibir apenas os documentos pendentes de envio.
class DocumentoFilterBackend(DjangoFilterBackend):
    class Meta:
        model = Documento

    def get_schema_fields(self, view):
        fields = super(DocumentoFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(
                name="pendentes",
                description='mostra só os documentos pendentes de envio',
                required=False, location='query', type='boolean'
            ),
        ]

        fields.extend(f)
        return fields


# adiciona campos de filtro para buscar pessoas assistidas com base em critérios como cpf,
class PessoaAssistidaFilterBackend(DjangoFilterBackend):
    class Meta:
        model = PessoaAssistida

    def get_schema_fields(self, view):
        fields = super(PessoaAssistidaFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(name="cpf", description='CPF sem pontuação', required=False, location='query', type='string'),
            coreapi.Field(name="nome", description='nome ou parte dele', required=False, location='query',
                          type='string'),
            coreapi.Field(name="apelido", description='apelido ou parte dele', required=False, location='query',
                          type='string'),
            coreapi.Field(name="nome_social", description='nome social ou parte dele', required=False, location='query',
                          type='string'),
        ]

        fields.extend(f)
        return fields


# adiciona campos de filtro para gerar horários disponíveis para agendamento de atendimentos.
class AtendimentoDefensorHorarioDisponivelParaAgendamentoFilterBackend(DjangoFilterBackend):
    class Meta:
        model = AtendimentoDefensor

    def get_schema_fields(self, view):
        fields = super(AtendimentoDefensorHorarioDisponivelParaAgendamentoFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(name="qnt", description='Quantidade horarios a ser gerado. Padrao é 4. Maximo é 50',
                          required=False, location='query', type='integer'),
            coreapi.Field(name="diasdiferentes", description='Força gerar os horarios dias diferentes',
                          required=False, location='query', type='boolean'),
        ]

        fields.extend(f)
        return fields


class ProcessoFilterBackend(DjangoFilterBackend):
    class Meta:
        model = Processo

    def get_schema_fields(self, view):
        fields = super(ProcessoFilterBackend, self).get_schema_fields(view)
        f = [
            # coreapi.Field(name="qnt", description='Quantidade horarios a ser gerado. Padrao é 4. Maximo é 50',
            #               required=False, location='query', type='integer'),
        ]

        fields.extend(f)
        return fields


# define um filtro personalizado para o modelo Indeferimento 
class IndeferimentoFilterBackend(DjangoFilterBackend):
    class Meta:
        model = Indeferimento
        fields = ('resultado', 'tipo_baixa')

    def get_schema_fields(self, view):
        fields = super(IndeferimentoFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(name="setor", description='Setor', required=True, location='query', type='integer'),
            coreapi.Field(name="prateleira", description='Prateleira', required=False, location='query', type='integer'),  # noqa: E501
            coreapi.Field(name="classe", description='Classe', required=False, location='query', type='integer'),
        ]

        fields.extend(f)
        return fields
