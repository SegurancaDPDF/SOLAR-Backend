# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0003_acordo_ativo'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='remarcado_auto',
            field=models.BooleanField(default=False),
        ),
    ]
