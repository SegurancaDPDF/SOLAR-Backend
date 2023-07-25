# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0032_fase_defensoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processo',
            name='grau',
            field=models.SmallIntegerField(default=0, choices=[(1, '1\xba Grau'), (2, '2\xba Grau'), (3, 'STF/STJ')]),
        ),
        migrations.AlterField(
            model_name='processo',
            name='numero',
            field=models.CharField(max_length=50, null=True, verbose_name='N\xfamero', blank=True),
        ),
        migrations.AlterField(
            model_name='processo',
            name='numero_puro',
            field=models.CharField(max_length=50, verbose_name='N\xfamero puro', db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='processo',
            unique_together=set([('numero_puro', 'grau')]),
        ),
    ]
