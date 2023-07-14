# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import io

from django.core.management.base import BaseCommand
import six

import json


class Command(BaseCommand):
    help = "Gera arquivo json dos Papeis Padrão a partir do arquivo 'initial_data_files/permissions.md'"

    def handle(self, *args, **options):

        groups = []

        with io.open(file='initial_data_files/permissions.md', mode='r', encoding='utf-8') as file:

            lines = file.readlines()

            for line in lines:

                data = line.replace('\n', '').split(';')
                itens = len(data)

                if itens == 1 and data[0]:

                    group = {
                        'name': data[0].replace('#', '').strip(),
                        'permissions': []
                    }

                    groups.append(group)
                    print('\n{}'.format(data[0]))

                elif itens == 3:

                    group['permissions'].append({
                        'app_label': data[0],
                        'model': data[1],
                        'codename': data[2],
                    })

                    print('{}_{}.{}'.format(data[0], data[1], data[2]))

        with io.open(file='initial_data_files/permissions.json', mode='w', encoding='utf-8') as json_file:
            data = json.dumps(groups, ensure_ascii=False)
            json_file.write(six.text_type(data))
