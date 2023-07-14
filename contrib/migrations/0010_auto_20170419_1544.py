# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0009_servidor_profissao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comarca',
            name='ativo',
            field=models.BooleanField(default=True, verbose_name='Ativo'),
        ),
        migrations.AlterField(
            model_name='defensoria',
            name='atuacao',
            field=models.CharField(default=None, max_length=1024, null=True, blank=True),
        ),
    ]
