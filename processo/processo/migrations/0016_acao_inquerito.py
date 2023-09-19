# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0015_auto_20170307_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='acao',
            name='inquerito',
            field=models.BooleanField(default=False, verbose_name='Inqu\xe9rito Policial'),
        ),
    ]
