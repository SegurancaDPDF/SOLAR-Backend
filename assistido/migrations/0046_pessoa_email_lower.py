# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from bulk_update.helper import bulk_update
from django.db import migrations, models
from django.db.models.functions import Length

from assistido.models import PerfilCamposObrigatorios


def migrate_data(apps, schema_editor):

    Pessoa = apps.get_model("assistido", "Pessoa")

    pessoas = Pessoa.objects.annotate(email_len=Length('email')).filter(email_len__gt=0)

    print('\nAplicando o lower no email dos assistidos...')

    for pessoa in pessoas:
        pessoa.email = pessoa.email.lower()

    print('Registrando alteracao no banco de dados...')
    if len(pessoas):
        bulk_update(pessoas, update_fields=['email'], batch_size=1000)

    print('Concluido!')


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0045_patrimonialtipo_grupo'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
        )
    ]
