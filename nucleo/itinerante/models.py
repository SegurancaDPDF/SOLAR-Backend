# -*- coding: utf-8 -*-
from datetime import datetime, date
from django.db import models


class Evento(models.Model):  # representa um evento no sistema

    titulo = models.CharField(max_length=256, null=True, blank=True, default=None)
    data_inicial = models.DateField('Data Início')
    data_final = models.DateField('Data Término')

    municipio = models.ForeignKey('contrib.Municipio', on_delete=models.DO_NOTHING)
    defensoria = models.ForeignKey('contrib.Defensoria', on_delete=models.DO_NOTHING)

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)

    data_autorizacao = models.DateTimeField('Data de Autorização', null=True, blank=False, editable=False)
    autorizado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                       editable=False, on_delete=models.DO_NOTHING)

    data_exclusao = models.DateTimeField('Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    participantes = models.ManyToManyField('contrib.Servidor')
    atuacoes = models.ManyToManyField('defensor.Atuacao')

    ativo = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'itinerante'
        verbose_name = u'Itinerante'
        verbose_name_plural = u'Itinerantes'
        ordering = ['-ativo', 'data_inicial', 'defensoria__comarca', ]
        permissions = (
            ('auth_evento', 'Can authorize evento'),
        )

    def __str__(self):
        return self.titulo

    def autorizar(self, autorizado_por):
        self.data_autorizacao = datetime.now()
        self.autorizado_por = autorizado_por
        self.save()

    def em_andamento(self):
        """Verifica se o evento está em andamento"""
        if self.data_inicial <= date.today() <= self.data_final:
            resposta = True
        else:
            resposta = False

        return resposta

    def excluir(self, excluido_por):
        self.data_exclusao = datetime.now()
        self.excluido_por = excluido_por
        self.ativo = False
        self.save()
