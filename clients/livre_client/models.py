# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
from django.db import models

# Módulos Solar
from core.models import AuditoriaAbstractMixin

logger = logging.getLogger(__name__)


# herda de 'AuditoriaAbstractMixin' para registrar o histórico de consultas da API
class HistoricoConsulta(AuditoriaAbstractMixin):

    ip = models.CharField('Endereço IP', max_length=15, null=True, blank=True, db_index=True)
    servico = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    parametros = models.JSONField(null=True, blank=True)
    resposta = models.TextField(null=True, blank=True, default=None)
    sucesso = models.BooleanField(default=False)

    class Meta:
        ordering = ['-cadastrado_em']
        verbose_name = u'Histórico de Consulta Livre API'
        verbose_name_plural = u'Históricos de Consulta Livre API'
