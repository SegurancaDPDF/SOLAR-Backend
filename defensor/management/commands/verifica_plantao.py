# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import datetime

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

# Solar
from defensor.services import consultar_api_plantao


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = u'Classe par verificação da API de plantões'

    def handle(self, *args, **options):
        try:
            consultar_api_plantao()
            logger.debug("Sucesso ao Acessar e carregar dados do plantão = %s \n" % (datetime.now()))
        except KeyError:
            logger.error("ERRO ao Acessar e carregar dados do plantão = %s \n" % (datetime.now()))
            pass
