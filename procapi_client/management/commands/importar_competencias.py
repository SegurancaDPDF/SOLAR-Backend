# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import datetime

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

# Modulos locais
from ...models import Competencia, SistemaWebService
from ...services import APICompetencia

logger = logging.getLogger(__name__)

# Função que realiza a importação das competências do PROCAPI para o SOLAR


class Command(BaseCommand):
    help = "Importa tabela competências do PROCAPI para o SOLAR"

    def handle(self, *args, **options):

        sistemas = SistemaWebService.objects.ativos().values('nome', 'id')

        for sistema in sistemas:

            itens = APICompetencia().listar_todos(params={'sistema_webservice': sistema['nome']})
            Competencia.objects.filter(sistema_webservice=sistema['id']).update(desativado_em=datetime.now())

            for item in itens:
                # Cria ou atualiza a competência no SOLAR com base nas informações do PROCAPI
                Competencia.objects.update_or_create(
                    codigo_mni=item['codigo'],
                    sistema_webservice_id=sistema['id'],
                    defaults={
                        'nome': item['nome'],
                        'desativado_em': None,
                        'desativado_por': None
                    }
                )

                print(u'"{}" ({}/{}) foi criada/atualizada com sucesso!'.format(
                    item['nome'],
                    item['codigo'],
                    item['sistema_webservice'],
                ))
