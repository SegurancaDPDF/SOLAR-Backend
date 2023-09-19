# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0010_auto_20160601_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentotipo',
            name='recurso',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='documentofase',
            name='nome',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='documentotipo',
            name='nome',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='fase',
            name='atividade',
            field=models.SmallIntegerField(default=0, choices=[(0, 'Outra'), (1, 'Audi\xeancia'), (2, 'J\xfari'), (3, 'Senten\xe7a'), (4, 'Recurso')]),
        ),
    ]
