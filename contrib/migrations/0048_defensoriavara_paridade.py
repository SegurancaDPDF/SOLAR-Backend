# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0047_defensoria_vara'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoriavara',
            name='paridade',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Qualquer'), (1, 'Processos \xcdmpares'), (2, 'Processos Pares')]),
        ),
    ]
