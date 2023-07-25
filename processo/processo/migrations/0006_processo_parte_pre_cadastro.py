# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0005_processo_pre_cadastro'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='parte_pre_cadastro',
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
    ]
