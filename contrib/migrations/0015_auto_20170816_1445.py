# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0014_auto_20170816_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defensoria',
            name='nome',
            field=models.CharField(max_length=255, db_index=True),
        ),
    ]
