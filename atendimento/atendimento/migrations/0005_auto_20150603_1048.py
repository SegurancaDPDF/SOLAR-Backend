# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0004_atendimento_remarcado_auto'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='prazo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='prioridade',
            field=models.BooleanField(default=False),
        ),
    ]
