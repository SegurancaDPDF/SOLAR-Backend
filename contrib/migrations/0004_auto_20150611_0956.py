# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0003_comarca_data_implantacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servidor',
            name='matricula',
            field=models.CharField(default='', max_length=32, blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='servidor',
            name='nome',
            field=models.CharField(default='', max_length=256, blank=True),
            preserve_default=False,
        ),
    ]
