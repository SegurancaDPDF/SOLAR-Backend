# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
from constance import config
from django.core.management.base import BaseCommand

# Modulos locais
from processo.processo.models import Assunto
from ...services import APIAssunto

logger = logging.getLogger(__name__)

# Esse código permite a importação dos assuntos do PROCAPI para o SOLAR,
# garantindo que os assuntos estejam atualizados e correspondam aos dados fornecidos pela API.


class Command(BaseCommand):
    help = "Importa tabela assuntos do PROCAPI para o SOLAR"

    def handle(self, *args, **options):
        WARNING = '\033[93m'
        ENDC = '\033[0m'

        itens = APIAssunto().listar_todos()

        for item in itens:

            ativo = item['ativo'] and not item['tem_filhos']

            try:
                # Atualizar ou criar o assunto com base no código CNJ
                Assunto.objects.update_or_create(
                    codigo_cnj=item['codigo'],
                    defaults={
                        'nome': item[config.PROCAPI_ASSUNTO_CAMPO_EXIBICAO],
                        'ativo': ativo
                    }
                )

                print(u'"{}" ({}) foi criado/atualizado com sucesso!'.format(
                    item['nome'],
                    item['codigo']
                ))
            # Se houver múltiplos objetos associados ao código CNJ, atualizar o estado de ativação
            except Assunto.MultipleObjectsReturned:

                total = Assunto.objects.filter(codigo_cnj=item['codigo']).update(ativo=ativo)

                print(WARNING + u'Existem {} assuntos vinculados ao código cnj "{}"!'.format(
                    total,
                    item['codigo']
                ) + ENDC)
