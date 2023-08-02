# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0010_auto_20170327_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='nome',
            field=models.CharField(max_length=256, db_index=True),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='nome_social',
            field=models.CharField(default=None, max_length=256, null=True, db_index=True, blank=True),
        ),
    ]
