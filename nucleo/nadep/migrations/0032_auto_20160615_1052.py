# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0031_falta_evento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historico',
            name='evento',
            field=models.SmallIntegerField(verbose_name='Evento', choices=[(1, 'Pris\xe3o'), (2, 'Soltura'), (3, 'Atendimento'), (4, 'Visita'), (5, 'Condena\xe7\xe3o'), (6, 'Falta'), (7, 'Regress\xe3o'), (8, 'Progress\xe3o'), (9, 'Mudan\xe7a de Regime'), (10, 'Transfer\xeancia'), (11, 'Conversao de Pena')]),
        ),
    ]
