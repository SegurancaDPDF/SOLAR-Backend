# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging

import re

try:
    from cStringIO import StringIO
except Exception:
    from StringIO import StringIO
import csv

# Bibliotecas de terceiros
from django.core.management.base import BaseCommand
import six
from constance import config

# Modulos locais
from ...models import Servidor
from ...services import consultar_api_athenas

logger = logging.getLogger(__name__)

CARACTERES_NUMERICOS = re.compile(r'[^0-9]')


class Command(BaseCommand):
    help = "Verificar divergencias de username entre solar e athenas"

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output', default='divergencias.csv', dest='output',
                            help='Specifies file to which the output is written.')

    def handle(self, *args, **options):
        output = options.get('output')
        try:
            servidores = Servidor.objects.select_related('usuario').all()

            cadastro_usuario_divergente = []
            if config.USAR_API_ATHENAS:
                logger.info('Consultando API Athenas')
                for s in servidores:
                    cpf = CARACTERES_NUMERICOS.sub('', s.cpf)
                    athenas_online, dados_api_por_cpf = consultar_api_athenas(cpf=cpf, buscar_supervisor=False)
                    if dados_api_por_cpf:
                        username_no_athenas = dados_api_por_cpf.get('username')
                        username_no_solar = s.usuario.username
                        if username_no_solar != username_no_athenas:
                            cadastro_usuario_divergente.append((s, dados_api_por_cpf))
                    else:
                        athenas_online, dados_api_por_matricula = consultar_api_athenas(matricula=s.matricula,
                                                                                        buscar_supervisor=False)
                        if dados_api_por_matricula:
                            username_no_athenas = dados_api_por_matricula.get('username')
                            username_no_solar = s.usuario.username
                            if username_no_solar != username_no_athenas:
                                cadastro_usuario_divergente.append((s, dados_api_por_matricula))

            logger.info('Gerando arquivo com divergencias')
            try:
                # self.stdout.ending = None
                stream = open(output, six.binary_type('w')) if output else StringIO()
                try:
                    with csv.writer(stream) as csv_writer:
                        csv_writer.writerow(('Nome', 'CPF Athenas', 'CPF Solar', 'Usuario Athenas', 'Usuario Solar'))
                        for servidor, athenas in cadastro_usuario_divergente:
                            csv_writer.writerow(
                                (servidor.nome, athenas.get('cpf'), servidor.cpf, athenas.get('username'),
                                 servidor.usuario.username))
                finally:
                    if stream:
                        stream.close()
            except Exception as e:
                pass
            else:
                if not output:
                    self.stdout.write(stream)
        except Exception as e:
            print(e)
