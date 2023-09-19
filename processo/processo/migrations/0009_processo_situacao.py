# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0008_auto_20151215_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='situacao',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Movimento'), (1, 'Baixado')]),
        ),
    ]
