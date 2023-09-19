# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0042_identidadegenero'),
        ('processo', '0031_fase_data_termino_protocolo'),
    ]

    operations = [
        migrations.AddField(
            model_name='fase',
            name='defensoria',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
