# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import datetime

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

# Modulos locais
from ...models import SistemaWebService
from ...services import APISistema

logger = logging.getLogger(__name__)

# Classe Command que permite a importação da tabela de sistemas webservice do PROCAPI para o SOLAR


class Command(BaseCommand):
    help = "Importa tabela sistemas webservice do PROCAPI o SOLAR"

    def handle(self, *args, **options):

        itens = APISistema().listar_todos()

        SistemaWebService.objects.update(desativado_em=datetime.now())

        for item in itens:
            # Cria ou atualiza o sistema web service no banco de dados
            SistemaWebService.objects.update_or_create(
                nome=item['nome'],
                defaults={
                    'desativado_em': None,
                    'desativado_por': None
                }
            )

            print(u'"{}" foi criado/atualizado com sucesso!'.format(
                item['nome'],
            ))
