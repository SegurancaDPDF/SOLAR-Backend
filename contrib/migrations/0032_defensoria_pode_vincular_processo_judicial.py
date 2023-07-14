# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0031_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='defensoria',
            options={'ordering': ['comarca__nome', 'nome', 'numero'], 'verbose_name': 'Defensoria', 'verbose_name_plural': 'Defensorias'},
        ),
        migrations.AddField(
            model_name='defensoria',
            name='pode_vincular_processo_judicial',
            field=models.BooleanField(default=True, help_text='Pode vincular processo judicial?'),
        ),
    ]
