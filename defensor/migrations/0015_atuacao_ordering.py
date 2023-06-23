# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0014_ajustes_campos_usuario_mni'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='atuacao',
            options={'ordering': ['defensoria__nome', 'defensor__servidor__nome', '-ativo', '-tipo', 'data_inicial'], 'verbose_name': 'Atua\xe7\xe3o', 'verbose_name_plural': 'Atua\xe7\xf5es'},
        ),
    ]
