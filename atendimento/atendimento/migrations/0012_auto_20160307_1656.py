# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0011_auto_20160203_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acordo',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Sim - Partes entraram em acordo'), (5, 'Sim - Acordo Subjetivo'), (1, 'N\xe3o - Partes n\xe3o entraram em acordo'), (2, 'N\xe3o - Requerente n\xe3o compareceu'), (3, 'N\xe3o - Requerido n\xe3o compareceu'), (4, 'N\xe3o - Ambas partes n\xe3o compareceram')]),
        ),
    ]
