# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0002_auto_20150527_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defensor',
            name='senha_eproc',
            field=models.CharField(default='', max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='usuario_eproc',
            field=models.CharField(default='', max_length=100, blank=True),
        ),
    ]
