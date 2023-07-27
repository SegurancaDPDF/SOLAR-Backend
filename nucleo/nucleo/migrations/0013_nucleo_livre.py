# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0012_auto_20180517_1501'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='livre',
            field=models.BooleanField(default=False),
        ),
    ]
