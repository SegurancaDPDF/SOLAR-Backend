# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('honorarios', '0004_analise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analise',
            name='motivo',
            field=models.CharField(default=None, max_length=255, null=True, verbose_name='Motivo pend\xeancia', blank=True),
        ),
    ]
