# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='data',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='documento',
            name='doe_data',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='numero',
            field=models.CharField(max_length=50),
        ),
    ]
