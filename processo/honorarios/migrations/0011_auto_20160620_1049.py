# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('honorarios', '0010_alertaprocessomovimento'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alertaprocessomovimento',
            options={'ordering': ['-ativo', '-data_cadastro'], 'verbose_name': 'Alerta de Movimentacao Honorario', 'verbose_name_plural': 'Alertas de Movimenta\xe7\xf5es Honorarios'},
        ),
    ]
