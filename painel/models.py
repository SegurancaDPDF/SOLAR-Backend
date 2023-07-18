# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

# Biblitecas de terceiros
import reversion
from django.db import models


# Solar

from core.models import AuditoriaAbstractMixin
# Modulos locais


logger = logging.getLogger(__name__)

# definir Painel


class Painel(AuditoriaAbstractMixin):

    TIPO_RECEPCAO = 0
    TIPO_DEFENSOR = 1

    LISTA_TIPO = (
        (TIPO_RECEPCAO, 'Painel da Recepção'),
        (TIPO_DEFENSOR, 'Painel do Defensor')
    )

    atendimento = models.ForeignKey('atendimento.Defensor', on_delete=models.PROTECT)
    predio = models.ForeignKey('comarca.Predio', on_delete=models.PROTECT)
    tipo = models.IntegerField(choices=LISTA_TIPO, default=TIPO_RECEPCAO, db_index=True)

    def __unicode__(self):
        return str(self.atendimento.numero)


reversion.register(Painel)
