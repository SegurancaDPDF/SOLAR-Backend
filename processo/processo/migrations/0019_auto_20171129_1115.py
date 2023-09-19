# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0018_auto_20171129_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processo',
            name='numero',
            field=models.CharField(db_index=True, max_length=50, null=True, verbose_name='N\xfamero', blank=True),
        ),
        migrations.AlterField(
            model_name='processo',
            name='numero_puro',
            field=models.CharField(db_index=True, max_length=50, null=True, verbose_name='N\xfamero puro', blank=True),
        ),
    ]
