# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0041_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='data_agendamento',
            field=models.DateTimeField(default=None, null=True, verbose_name='Data do agendamento', db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='data_atendimento',
            field=models.DateTimeField(default=None, null=True, verbose_name='Data do atendimento', db_index=True, blank=True),
        ),
    ]
