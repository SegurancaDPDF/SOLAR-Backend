# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields
from datetime import datetime


def migrate_data(apps, schema_editor):
    Arvore = apps.get_model("atendimento", "Arvore")
    total = Arvore.objects.filter(ativo=True).update(ativo=False)
    print('\n{} arvores invalidadas!'.format(total))


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0089_functions_relatorios_atividades'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=migrate_data,
            atomic=True
        ),
    ]
