# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0004_auto_20160510_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='cpf',
            field=models.CharField(default=None, max_length=32, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='nome_norm',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
        ),
    ]
