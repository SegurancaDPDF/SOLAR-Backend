# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.db import models
from django.db.models import deletion


# modelo de bd que representa um guichê ou sala
class Guiche(models.Model):
    # constantes para o tipo de guichê ou sala
    GUICHE = 1
    SALA = 2
    LISTA_TIPO = (
        (GUICHE, 'Guichê'),
        (SALA, 'Sala')
    )
    # campos do modelo Guiche
    tipo = models.SmallIntegerField('Tipo de guichê', choices=LISTA_TIPO, null=True, blank=True, default=1)
    numero = models.IntegerField('Número', default=0)
    comarca = models.ForeignKey('contrib.Comarca', on_delete=deletion.PROTECT)
    predio = models.ForeignKey('comarca.Predio', null=True, blank=True, on_delete=deletion.PROTECT)
    defensoria = models.ForeignKey('contrib.Defensoria', null=True, blank=True, on_delete=deletion.PROTECT)
    andar = models.SmallIntegerField('Qual andar?', null=True, blank=True, default=0)
    usuario = models.ForeignKey('contrib.Servidor', null=True, blank=True, on_delete=deletion.PROTECT)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return str(self.numero)

    class Meta:
        verbose_name = u'Guichê'
        ordering = ['comarca__nome', 'predio__nome', 'numero']


class Predio(models.Model):
    comarca = models.ForeignKey('contrib.Comarca', related_name='predios', on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=255)
    endereco = models.ForeignKey('contrib.Endereco', null=True, blank=True, on_delete=models.DO_NOTHING)
    telefone = models.ForeignKey('contrib.Telefone', null=True, blank=True, on_delete=models.DO_NOTHING)
    visao_comarca = models.BooleanField(default=False)
    recepcao_por_atuacao = models.BooleanField('Recepção mostrar apenas atuações do servidor?', default=False)
    qtd_andares = models.PositiveSmallIntegerField(
        verbose_name='Quantidade de andares',
        help_text='Deixar zero caso tenha somente o térreo',
        null=True,
        blank=True,
        default=0
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return "%s - %s" % (self.comarca, self.nome)

    class Meta:
        verbose_name = u'Prédio'
        ordering = ['comarca__nome', 'nome']
