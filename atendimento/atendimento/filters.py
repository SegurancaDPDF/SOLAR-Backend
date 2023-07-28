# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import coreapi
from django_filters.rest_framework import DjangoFilterBackend

from . import models


# backend de filtro personalizado para o modelo de Qualificacao
class QualificacaoFilterBackend(DjangoFilterBackend):
    class Meta:
        model = models.Qualificacao

    # retorna os campos de esquema para o filtro da Qualificação
    def get_schema_fields(self, view):
        fields = super(QualificacaoFilterBackend, self).get_schema_fields(view)
        f = [
            coreapi.Field(
                name="disponivel_para_agendamento_via_app",
                description='Disponível para agendamento via apps (Luna, eDefensor, etc)?',
                required=False, location='query', type='boolean'
            ),
            coreapi.Field(
                name="exibir_em_atendimentos",
                description='Lista apenas qualificações disponíveis em atendimento',
                required=False, location='query', type='boolean'
            ),
            coreapi.Field(
                name="tipo",
                description='Tipo da qualificação',
                required=False, location='query', type='integer'
            ),
            coreapi.Field(
                name="penal",
                description='Vinculada a uma área penal?',
                required=False, location='query', type='boolean'
            ),
            coreapi.Field(
                name="orgao_encaminhamento",
                description='Órgão de encaminhamento',
                required=False, location='query', type='integer'
            ),
            coreapi.Field(
                name="possui_orgao_encaminhamento",
                description='Possui órgão de encaminhamento',
                required=False, location='query', type='boolean'
            ),
        ]

        fields.extend(f)
        return fields