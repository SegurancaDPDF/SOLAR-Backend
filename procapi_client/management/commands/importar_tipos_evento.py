# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import datetime

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

# Modulos locais
from ...models import TipoEvento, SistemaWebService
from ...services import APITipoEvento

logger = logging.getLogger(__name__)

# Classe Command que permite a importação da tabela tipos de evento do PROCAPI para tabela tipos de evento do SOLAR


class Command(BaseCommand):
    help = "Importa tabela tipos de evento do PROCAPI para tabela tipos de evento do SOLAR"

    def handle(self, *args, **options):

        sistemas = SistemaWebService.objects.ativos().values('nome', 'id')

        for sistema in sistemas:

            itens = APITipoEvento().listar_todos(params={'sistema_webservice': sistema['nome']})
            TipoEvento.objects.filter(sistema_webservice=sistema['id']).update(desativado_em=datetime.now())

            for item in itens:
                # Cria ou atualiza o tipo de evento no banco de dados
                TipoEvento.objects.update_or_create(
                    codigo_mni=item['codigo'],
                    sistema_webservice_id=sistema['id'],
                    defaults={
                        'nome': item['nome'],
                        'disponivel_em_peticao_avulsa': item['disponivel_em_peticao_avulsa'],
                        'disponivel_em_peticao_com_aviso': item['disponivel_em_peticao_com_aviso'],
                        'desativado_em': None,
                        'desativado_por': None
                    }
                )

                print(u'"{}" ({}/{}) foi criado/atualizado com sucesso!'.format(
                    item['nome'],
                    item['codigo'],
                    item['sistema_webservice'],
                ))
