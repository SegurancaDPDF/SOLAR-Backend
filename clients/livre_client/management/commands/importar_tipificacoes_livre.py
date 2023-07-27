# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

# Modulos locais
from nucleo.nadep.models import Tipificacao
from ...services import APILeiArtigoParagrafo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Importa tipificações do LIVRE/SEEU"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--incluir-paragrafo',
            action='store_true',
            help='Cria uma tipificação para cada parágrafo (lei/artigo/parágrafo)',
        )

    def handle(self, *args, **options):

        sucesso, resposta = APILeiArtigoParagrafo().consultar()

        if not sucesso:
            print(resposta)
            return False

        total = 0
        incluir_paragrafo = options['incluir_paragrafo']

        for item in resposta:

            params = {
                'numero_lei': item['numeroLei'],
                'artigo_lei': item['numeroArtigo']
            }

            if incluir_paragrafo:
                if item['numeroParagrafo'].isdigit():
                    params['paragrafo_lei'] = item['numeroParagrafo']
                else:
                    params['paragrafo_lei'] = None

            if not Tipificacao.objects.ativos().filter(**params).exists():

                # Gera nome da tipificação
                if incluir_paragrafo:

                    if item['numeroParagrafo'].isdigit():
                        params['nome'] = 'Art. {}, § {}º, {}: {}'.format(item['numeroArtigo'], item['numeroParagrafo'], item['nomeLei'], item['descricaoParagrafo'])
                    else:
                        params['nome'] = 'Art. {}, {}, {}: {}'.format(item['numeroArtigo'], item['numeroParagrafo'], item['nomeLei'], item['descricaoParagrafo'])

                else:
                    if item['descricaoArtigo'] is None:
                        descricao_artigo = 'sem descrição'
                        params['nome'] = 'Art. {}, {}: {}'.format(item['numeroArtigo'], item['nomeLei'], descricao_artigo)
                    else:
                        # Separa número da descrição do artigo separado por dois pontos (:)
                        descricao_artigo = item['descricaoArtigo'].split(':')

                        # Separa número da descrição do artigo separado por traço (-)
                        if len(descricao_artigo) == 1:
                            descricao_artigo = item['descricaoArtigo'].split(' - ')

                        # Obtém descrição do artigo sem o número
                        if len(descricao_artigo) > 1:
                            descricao_artigo = descricao_artigo[1]
                        else:
                            descricao_artigo = descricao_artigo[0]

                        params['nome'] = 'Art. {}, {}: {}'.format(item['numeroArtigo'], item['nomeLei'], descricao_artigo)

                params['nome'] = ' '.join(params['nome'].split())

                Tipificacao.objects.create(**params)
                total += 1

                print('"{}" foi importada com sucesso!'.format(params['nome']))

        print('{} tipificações foram importadas com sucesso!'.format(total))
