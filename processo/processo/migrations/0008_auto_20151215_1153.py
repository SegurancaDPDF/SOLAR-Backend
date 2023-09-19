# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0007_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='acao',
            name='execucao_penal',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='fase',
            name='processo',
            field=models.ForeignKey(related_name='fases', default=None, blank=True, to='processo.Processo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
