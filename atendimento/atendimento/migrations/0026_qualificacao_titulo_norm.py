# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0025_vw_atendimentos_dia'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualificacao',
            name='titulo_norm',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
        ),
    ]
