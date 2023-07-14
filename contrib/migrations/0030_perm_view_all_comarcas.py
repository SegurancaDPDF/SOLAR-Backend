# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0029_redimensiona_foto_servidores'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comarca',
            options={'ordering': ['-ativo', 'nome'], 'verbose_name': 'Comarca', 'verbose_name_plural': 'Comarcas', 'permissions': (('view_all_comarcas', 'Pode ver todas comarcas'),)},
        ),
    ]
