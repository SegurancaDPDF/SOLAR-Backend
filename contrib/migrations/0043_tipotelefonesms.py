# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0042_identidadegenero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telefone',
            name='tipo',
            field=models.SmallIntegerField(choices=[(0, 'Celular'), (1, 'Residencial'), (2, 'Comercial'), (3, 'Recado'), (4, 'WhatsApp'), (5, 'SMS')]),
        ),
    ]
