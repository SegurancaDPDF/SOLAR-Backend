# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

import re
# Bibliotecas de terceiros
from bulk_update.helper import bulk_update
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

# Modulos locais
from ...models import Servidor
from ...validators import validate_CPF

logger = logging.getLogger(__name__)

CARACTERES_NUMERICOS = re.compile(r'[^0-9]')


class Command(BaseCommand):
    help = "Normaliza cadastros de CPF. Remove caracteres não numericos e valida CPF. Se CPF invalido, muda valor para 0"  # noqa: E501

    def handle(self, *args, **options):
        try:
            servidores = Servidor.objects.select_related('usuario').all()
            logger.info('removendo caracteres não numéricos do CPF e validando CPF')
            for s in servidores:
                if s.cpf:
                    # remove caracteres não numéricos do CPF
                    s.cpf = CARACTERES_NUMERICOS.sub('', s.cpf)
            logger.info(
                'iniciando update contrib.models.Servidor no banco para remover caracteres não numericos de CPF')
            bulk_update(servidores, update_fields=['cpf'], batch_size=100)

            logger.info('validando CPF')
            for s in servidores:
                if s.cpf:
                    try:
                        validate_CPF(s.cpf)
                    except ValidationError:
                        s.cpf = 0

            bulk_update(servidores, update_fields=['cpf'], batch_size=100)

        except Exception as e:
            print(e)
