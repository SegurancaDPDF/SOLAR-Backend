# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import datetime

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

# Modulos locais
from ...services import FaseService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = u'Classe par verificação de processos eproc'

    def handle(self, *args, **options):
        try:
            fase_eproc = FaseService()
            fase_eproc.set_plantao()
            logger.debug("Sucesso ao carregar plantão em %s \n" % (datetime.now()))
        except Exception:
            logger.error("Erro ao carregar plantão em %s \n" % (datetime.now()))
            pass
