# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import migrations, models
from contrib.services import PapelService

def migrate_data(apps, schema_editor):
    service = PapelService()
    service.criar_papeis()

def reverse_migrate_data(apps, schema_editor):

    Papel = apps.get_model("contrib", "Papel")
    Papel.objects.filter(nome__startswith='Papel:').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0022_add_nome_telefone_para_contato'),
        ('core', '0003_cria_grupos_de_permissao_padrao'),
    ]

    operations = [
        # migrations.RunPython(
        #     code=migrate_data,
        #     reverse_code=reverse_migrate_data,
        #     atomic=True
        # ),
    ]
