# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='codigo',
            field=models.CharField(default=None, max_length=25, null=True, verbose_name='C\xf3digo', blank=True),
        ),
    ]
