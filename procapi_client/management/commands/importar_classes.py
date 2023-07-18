# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

# Modulos locais
from processo.processo.models import Acao
from ...services import APIClasse

logger = logging.getLogger(__name__)

# Esse código permite a importação das classes do PROCAPI para o SOLAR,
# garantindo que as ações estejam atualizadas e correspondam aos dados fornecidos pela API.


class Command(BaseCommand):
    help = "Importa tabela classes do PROCAPI para o SOLAR"

    def handle(self, *args, **options):
        WARNING = '\033[93m'
        ENDC = '\033[0m'

        itens = APIClasse().listar_todos()

        for item in itens:

            ativo = item['ativo'] and not item['tem_filhos']

            try:
                # Atualizar ou criar a ação com base no código CNJ
                Acao.objects.update_or_create(
                    codigo_cnj=item['codigo'],
                    defaults={
                        'nome': item['nome'],
                        'judicial': True,
                        'ativo': ativo
                    }
                )

                print(u'"{}" ({}) foi criada/atualizada com sucesso!'.format(
                    item['nome'],
                    item['codigo']
                ))
            # Se houver múltiplas ações associadas ao código CNJ, atualizar o estado de ativação
            except Acao.MultipleObjectsReturned:

                total = Acao.objects.filter(codigo_cnj=item['codigo']).update(ativo=ativo)

                print(WARNING + u'Existem {} tipos de ações vinculados ao código cnj "{}"!'.format(  # noqa: E501
                    total,
                    item['codigo']
                ) + ENDC)
