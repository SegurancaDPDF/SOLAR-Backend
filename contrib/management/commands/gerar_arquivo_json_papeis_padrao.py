# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import io

from django.core.management.base import BaseCommand
import six

import json


class Command(BaseCommand):
    help = "Gera arquivo json dos Papeis Padrão a partir do arquivo 'initial_data_files/papeis.md'"

    def handle(self, *args, **options):

        papeis = []

        with io.open(file='initial_data_files/papeis.md', mode='r', encoding='utf-8') as file:

            lines = file.readlines()

            for line in lines:

                data = line.replace('\n', '').split(';')

                if data[0]:

                    if data[0].startswith('#'):
                        papel = {
                            'name': data[0].replace('#', '').strip(),
                            'groups': []
                        }

                        papeis.append(papel)
                        print('\n{}'.format(data[0]))

                    else:

                        papel['groups'].append(data[0])
                        print('{}'.format(data[0]))

        with io.open(file='initial_data_files/papeis.json', mode='w', encoding='utf-8') as json_file:
            data = json.dumps(papeis, ensure_ascii=False)
            json_file.write(six.text_type(data))
