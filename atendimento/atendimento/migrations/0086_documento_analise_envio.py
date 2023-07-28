# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0042_identidadegenero'),
        ('atendimento', '0085_forma_atendimento'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='analisado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documento',
            name='analisar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='documento',
            name='data_analise',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
