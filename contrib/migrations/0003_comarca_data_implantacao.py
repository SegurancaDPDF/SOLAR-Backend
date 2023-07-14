# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0002_defensoria_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='comarca',
            name='data_implantacao',
            field=models.DateTimeField(null=True, verbose_name='Data da implanta\xe7\xe3o', blank=True),
        ),
    ]
