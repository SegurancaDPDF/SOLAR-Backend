# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_cria_grupos_de_permissao_padrao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classe',
            name='tipo',
            field=models.PositiveSmallIntegerField(
                default=8,
                choices=[
                    (8, 'Pedido'),
                    (6030, 'Impedimento'),
                    (6040, 'Suspei\xe7\xe3o'),
                    (6050, 'Nega\xe7\xe3o'),
                    (6051, 'Nega\xe7\xe3o por Hipossufici\xeancia'),
                    (6052, 'Denega\xe7\xe3o de Procedimento')
                ]
            ),
        ),
    ]
