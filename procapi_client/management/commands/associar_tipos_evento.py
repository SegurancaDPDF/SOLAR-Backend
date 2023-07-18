# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import datetime

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand

# Modulos locais
from ...models import TipoEvento
from processo.processo.models import FaseTipo

logger = logging.getLogger(__name__)

# Classe responsável por implementar um comando personalizado no Django para associação de tipos de evento.


class Command(BaseCommand):
    help = "Associa tipos de evento com aos tipos de fase atráves dos campos 'codigo_eproc' ou 'nome_norm'"

    def add_arguments(self, parser):
        # Método chamado para adicionar argumentos opcionais ao comando
        parser.add_argument(
            '--criar-tipo-fase',
            action='store_true',
            help='Cria tipo de fase se não houver correspondência com o tipo de evento',
        )

    def handle(self, *args, **options):
        WARNING = '\033[93m'
        ENDC = '\033[0m'

        # Tenta vincular tipos de fase aos tipos de evento com o codigo mni igual ao codigo_eproc do tipo da fase
        tipos_fase = FaseTipo.objects.all().exclude(codigo_eproc=None)

        for tipo_fase in tipos_fase:

            if tipo_fase.codigo_eproc.strip().isnumeric():

                tipos_evento = TipoEvento.objects.filter(codigo_mni=int(tipo_fase.codigo_eproc.strip()))

                for tipo_evento in tipos_evento:
                    tipo_fase.tipos_de_evento.add(tipo_evento)
                    tipo_fase.save()

                    print(u'"{}" vinculado a "{}" pelo código {}'.format(
                        tipo_fase,
                        tipo_evento,
                        tipo_fase.codigo_eproc
                    ))

        # Tenta vincular os tipos de fase aos tipos de evento com o mesmo nome
        tipos_fase = FaseTipo.objects.all().filter(tipos_de_evento=None).exclude(nome_norm=None)

        for tipo_fase in tipos_fase:

            tipos_evento = TipoEvento.objects.filter(nome_norm=tipo_fase.nome_norm)

            for tipo_evento in tipos_evento:
                tipo_fase.tipos_de_evento.add(tipo_evento)
                tipo_fase.save()
                print(u'"{}" vinculado a "{}" pelo nome'.format(tipo_fase, tipo_evento))

        # Tenta vincular os tipos de evento aos tipos de fase com o mesmo nome
        tipos_evento = TipoEvento.objects.ativos().filter(tipos_de_fase=None)

        for tipo_evento in tipos_evento:

            tipo_fase = FaseTipo.objects.filter(nome_norm=tipo_evento.nome_norm).order_by('-desativado_em', 'id').first()  # noqa: E501

            if tipo_fase:
                tipo_fase.tipos_de_evento.add(tipo_evento)
                print(u'"{}" vinculado a "{}" pelo nome'.format(tipo_fase, tipo_evento))

        # Procura por tipos de evento sem correspondência aos tipos de fases depois das comparações
        tipos_evento = TipoEvento.objects.ativos().filter(tipos_de_fase=None)

        # Se argumento informado, cria tipos de fase para tipos de eventos onde não houve correspondência
        if options['criar_tipo_fase']:

            desativado_em = datetime.now()

            for tipo_evento in tipos_evento:

                tipo_fase = FaseTipo.objects.create(
                    nome=tipo_evento.nome,
                    codigo_eproc=tipo_evento.codigo_mni,
                    judicial=True,
                    desativado_em=desativado_em
                )

                tipo_fase.tipos_de_evento.add(tipo_evento)

                print(u'"{}" criado e vinculado a "{}" pelo nome'.format(tipo_fase, tipo_evento))

        elif tipos_evento.count():

            print(WARNING + u'{} tipos de eventos sem correspondência, para criar o tipo de fase, execute este comando novamente com o comando --criar-tipo-fase'.format(  # noqa: E501
                tipos_evento.count()
            ) + ENDC)

        print(u'Concluído!')
