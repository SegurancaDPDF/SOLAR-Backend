# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('honorarios', '0011_auto_20160620_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='honorario',
            name='suspenso',
            field=models.BooleanField(default=False, verbose_name='Suspenso?'),
        ),
        migrations.AddField(
            model_name='honorario',
            name='suspenso_ate',
            field=models.DateField(default=None, null=True, verbose_name='Suspenso at\xe9', blank=True),
        ),
        migrations.AlterField(
            model_name='movimento',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Anota\xe7\xe3o'), (1, 'Aguardando Peticionamento'), (2, 'Peti\xe7\xe3o'), (3, 'Encaminhado ao Defensor'), (4, 'Protocolo'), (5, 'Baixa'), (6, 'Suspens\xe3o')]),
        ),
    ]
