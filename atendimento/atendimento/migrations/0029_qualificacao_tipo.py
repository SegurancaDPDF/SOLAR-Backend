# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0028_atendimento_participantes'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualificacao',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=10, choices=[(10, 'Pedido'), (20, 'Atividade')]),
        ),
    ]
