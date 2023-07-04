# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations, models
from contrib.services import PapelService

def migrate_data(apps, schema_editor):
    service = PapelService()
    service.criar_grupos()

def reverse_migrate_data(apps, schema_editor):

    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__startswith='Permissão:').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alteracoes_indices'),
    ]

    operations = [
        # migrations.RunPython(
        #     code=migrate_data,
        #     reverse_code=reverse_migrate_data,
        #     atomic=True
        # ),
    ]
