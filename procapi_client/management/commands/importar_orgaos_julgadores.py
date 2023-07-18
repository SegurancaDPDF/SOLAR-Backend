# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime  # isort:skip

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

# Modulos locais
from ...services import APIOrgaoJulgador
from ...models import OrgaoJulgador, SistemaWebService

logger = logging.getLogger(__name__)

# Classe Command que realiza a importação dos órgãos julgadores do PROCAPI para o SOLAR
# garantindo que as informações estejam atualizadas no sistema.


class Command(BaseCommand):
    help = "Importa tabela órgãos julgadores do PROCAPI o SOLAR"

    def handle(self, *args, **options):

        sistemas = SistemaWebService.objects.ativos().values('nome', 'id')

        for sistema in sistemas:

            itens = APIOrgaoJulgador().listar_todos(params={'sistema_webservice': sistema['nome']})
            # Define a data de desativação para os órgãos julgadores do sistema no banco de dados
            OrgaoJulgador.objects.filter(sistema_webservice=sistema['id']).update(desativado_em=datetime.now())

            for item in itens:
                # Cria ou atualiza o órgão julgador no banco de dados
                OrgaoJulgador.objects.update_or_create(
                    codigo_mni=item['codigo'],
                    sistema_webservice_id=sistema['id'],
                    defaults={
                        'nome': item['nome'],
                        'desativado_em': None,
                        'desativado_por': None
                    }
                )

                print(u'"{}" ({}/{}) foi criado/atualizado com sucesso!'.format(
                    item['nome'],
                    item['codigo'],
                    item['sistema_webservice'],
                ))
