# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0007_auto_20160928_0858'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profissao',
            options={'ordering': ['nome', 'codigo'], 'verbose_name': 'Profiss\xe3o', 'verbose_name_plural': 'Profiss\xf5es'},
        ),
    ]
