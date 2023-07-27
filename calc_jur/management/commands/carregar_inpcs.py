# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand
from calc_jur.models import Inpc
from datetime import datetime
import requests


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Carregar os índices do INPC para ser utilizado na calculadora jurídica"

    def handle(self, *args, **options):
        # ano e mes do primeiro registro de inpc disponivel na api do IBGE
        ano = 1979
        mes = 4

        # ano e mes atual - até onde o loop deve iterar
        ano_atual = int(datetime.today().year)
        # fazer do ano_mes 197902 até a data atual - por exemplo 202301
        while ano <= ano_atual:
            # monta ano_mes do tipo string - padrao YYYYMM
            ano_str = str(ano)
            if mes < 10:
                mes_str = '0' + str(mes)
            else:
                mes_str = str(mes)
            ano_mes = ano_str + mes_str

            # processa o ano_mes - verifica se nao tem na base, e se nao tiver, insere conforme carregado da api do IBGE
            inpc_ja_cadastrado = self.vericar_inpc(ano_mes)

            if inpc_ja_cadastrado:
                # significa que o mes ja foi carregado do service remoto em algum momento anterior
                print('ano mês {} já existe na base'.format(ano_mes))
            else:
                # significa que precisaremos carregar o valor do inpc deste mês e ano e salvar na base local
                print('ano mes ' + ano_mes + ' nao existe na base. Carregando do servidor remoto... ')

                url = 'http://servicodados.ibge.gov.br/api/v3/agregados/1736/periodos/' \
                    '{0}/variaveis/44?localidades=N1[1]'.format(ano_mes)

                r = requests.get(url).json()
                ano_mes_str = str(ano_mes)
                try:
                    inpc = (r[0]['resultados'][0]['series'][0]['serie'][ano_mes_str])
                    print(inpc)

                    # salvar na base de dados
                    self.salvar_inpc(ano_mes, inpc)
                except Exception:
                    print('valor remoto do inpc do ano mês ' + ano_mes_str + ' nao disponivel')

            # itera o mes/ano seguinte
            mes += 1
            if mes > 12:
                mes = 1
                ano += 1

    def vericar_inpc(self, ano_mes):
        print('entrou vericar_inpc')
        try:
            return Inpc.objects.filter(ano_mes=ano_mes).exists()
        except Exception as error:
            print(error.args[0])

    def salvar_inpc(self, ano_mes, valor):
        print('entrou salvar_inpc')
        try:

            Inpc.objects.create(
                ano_mes=ano_mes,
                valor=valor
            )
            print("records inserted")
        except Exception as error:
            print(error.args[0])
