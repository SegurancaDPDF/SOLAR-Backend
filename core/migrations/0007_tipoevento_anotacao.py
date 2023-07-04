# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_processo_setores_notificados'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipoevento',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=8, choices=[(8, 'Peti\xe7\xe3o'), (9, 'Recurso'), (10, 'Encaminhamento'), (11, 'Recebimento'), (12, 'Decis\xe3o'), (13, 'Baixa'), (16, 'Anota\xe7\xe3o')]),
        ),
    ]
