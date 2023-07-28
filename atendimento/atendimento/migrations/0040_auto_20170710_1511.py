# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0039_auto_20170629_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=0, db_index=True, choices=[(0, 'Liga\xe7\xe3o'), (1, 'Inicial'), (2, 'Retorno'), (3, 'Recep\xe7\xe3o'), (4, 'Apoio de N\xfacleo Especializado'), (5, 'Anota\xe7\xe3o'), (6, 'Processo'), (7, 'Visita ao Preso'), (8, 'Atendimento ao Interessado'), (9, 'Encaminhamento'), (10, 'Atividade')]),
        ),
    ]
