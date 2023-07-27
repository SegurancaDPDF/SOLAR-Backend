# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0040_auto_20161025_0845'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tipificacao',
            options={'ordering': ['-ativo', 'nome'], 'verbose_name': 'Tipifica\xe7\xe3o', 'verbose_name_plural': 'Tipifica\xe7\xf5es'},
        ),
    ]
