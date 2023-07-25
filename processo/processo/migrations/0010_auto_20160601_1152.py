# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0009_processo_situacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parte',
            name='atendimento',
            field=models.ForeignKey(default=None, blank=True, to='atendimento.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
