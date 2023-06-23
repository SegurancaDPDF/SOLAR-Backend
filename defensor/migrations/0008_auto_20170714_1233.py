# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0007_defensor_eh_defensor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atuacao',
            name='tipo',
            field=models.SmallIntegerField(default=2, choices=[(0, 'Substitui\xe7\xe3o'), (1, 'Acumula\xe7\xe3o'), (2, 'Titularidade'), (3, 'Lota\xe7\xe3o')]),
        ),
    ]
