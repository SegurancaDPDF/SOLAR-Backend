# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0018_idx_atendimento_atendimento_data_cadastro_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='arvore',
            name='ativo',
            field=models.BooleanField(default=True),
        ),
    ]
