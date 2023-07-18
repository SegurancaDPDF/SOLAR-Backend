# -*- coding: utf-8 -*-
# Importações necessárias

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.db import models

from core.models import AuditoriaAbstractMixin
from contrib.models import Servidor
from .managers import TermoRespostaManager

# Definição do modelo Termo


class Termo(AuditoriaAbstractMixin):

    UNICO = 'un'
    MULTIPLA = 'mu'

    TIPO_RESPOSTA_CHOICES = (
        (UNICO, 'Única'),
        (MULTIPLA, 'Multipla'),
    )

    TIPO_TEXTO_PURO = 'txt'
    TIPO_TEXTO_HTML = 'html'

    TIPO_TEXTO_CHOICES = (
        (TIPO_TEXTO_PURO, 'Texto Puro'),
        (TIPO_TEXTO_HTML, 'Texto HTML'),
    )

# Campos do modelo Termo

    titulo = models.CharField(verbose_name='Titulo', max_length=255)
    descricao = models.TextField(verbose_name='Descrição')
    servidores = models.ManyToManyField(Servidor, through='TermoResposta', through_fields=('termo', 'servidor'))
    tipo_resposta = models.CharField("Tipo de Resposta", choices=TIPO_RESPOSTA_CHOICES, max_length=10)
    tipo_descricao = models.CharField(choices=TIPO_TEXTO_CHOICES, default=TIPO_TEXTO_PURO, max_length=5)
    data_inicio = models.DateField(verbose_name='Data de Início', null=True, blank=True)
    data_finalizacao = models.DateField(verbose_name='Data de Finalização', null=True, blank=True)

    class Meta:
        verbose_name = u'Termo'
        verbose_name_plural = u'Termos'
        ordering = ['cadastrado_em']

    def __str__(self):
        return self.titulo

# Definição do modelo TermoResposta


class TermoResposta(AuditoriaAbstractMixin):
    termo = models.ForeignKey(Termo, on_delete=models.PROTECT)
    servidor = models.ForeignKey(Servidor, on_delete=models.PROTECT)
    titulo_termo = models.CharField(verbose_name='Titulo', max_length=255, editable=False)
    descricao_termo = models.TextField(verbose_name='Descrição', editable=False)
    aceite = models.BooleanField()
    data_resposta = models.DateTimeField(verbose_name='Data de Cadastro', null=True, blank=False, auto_now_add=True)

    objects = TermoRespostaManager()

    class Meta:
        verbose_name = u'Resposta de Termo'
        verbose_name_plural = u'Respostas dos Termos'
        ordering = ['data_resposta']

    def __str__(self):
        return '{} - {}'.format(self.termo.titulo, self.servidor.nome)
