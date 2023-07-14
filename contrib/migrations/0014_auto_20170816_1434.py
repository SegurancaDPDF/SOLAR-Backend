# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0013_add_model_papel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servidor',
            name='nome',
            field=models.CharField(db_index=True, max_length=256, blank=True),
        ),
    ]
