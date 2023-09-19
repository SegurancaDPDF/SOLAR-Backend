# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0023_auto_20180228_0943'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assunto',
            options={'ordering': ['-ativo', 'nome'], 'verbose_name': 'Assunto', 'verbose_name_plural': 'Assuntos'},
        ),
    ]
