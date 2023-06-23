# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0010_atuacao_cargo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='atuacao',
            options={'ordering': ['defensoria__nome', 'defensor__servidor__usuario__first_name', '-ativo', '-tipo', 'data_inicial'], 'verbose_name': 'Atua\xe7\xe3o', 'verbose_name_plural': 'Atua\xe7\xf5es'},
        ),
    ]
