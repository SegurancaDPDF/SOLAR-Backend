# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0098_qualificacao_remover_duplicadas_sem_titulo'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='interesse_conciliacao',
            field=models.PositiveSmallIntegerField(null=True, choices=[(10, 'Na Defensoria'), (20, 'Perante a justi\xe7a')]),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='justificativa_nao_interesse',
            field=models.TextField(default='', null=True, blank=True),
        ),
    ]
