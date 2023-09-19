# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0011_auto_20160614_1434'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documentotipo',
            options={'ordering': ['-ativo', 'nome', 'grau'], 'verbose_name': 'Tipo de Documento', 'verbose_name_plural': 'Tipos de Documento'},
        ),
    ]
