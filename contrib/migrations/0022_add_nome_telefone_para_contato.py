# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0021_remove_servidor_profissao'),
    ]

    operations = [
        migrations.AddField(
            model_name='telefone',
            name='nome',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
