# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0002_auto_20150525_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='acordo',
            name='ativo',
            field=models.BooleanField(default=True),
        ),
    ]
