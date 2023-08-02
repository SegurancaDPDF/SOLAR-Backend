# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
from bulk_update.helper import bulk_update
from django.core.management.base import BaseCommand

# Modulos locais
from ...models import Filiacao, Pessoa


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Regera nome_soundex para models assistido.models.Pessoa e assistido.models.Filiacao"

    def handle(self, *args, **options):
        try:
            pessoas = Pessoa.objects.all()
            logger.info('regerando nome_soundex assistido.models.Pessoa:')
            for p in pessoas:
                p.nome_soundex = p.soundex()
            logger.info('iniciando update assistido.models.Pessoa no banco')
            bulk_update(pessoas, update_fields=['nome_soundex'], batch_size=1000)
            logger.info('finalizado update assistido.models.Pessoa no banco')

            # Filiacao
            filiacoes = Filiacao.objects.all()
            logger.info('regerando nome_soundex assistido.models.Filiacao:')
            for f in filiacoes:
                f.nome_soundex = f.soundex()
            logger.info('iniciando update assistido.models.Filiacao no banco')
            bulk_update(filiacoes, update_fields=['nome_soundex'], batch_size=1000)
            logger.info('finalizado update assistido.models.Filiacao no banco')
        except Exception as e:
            print(e)
