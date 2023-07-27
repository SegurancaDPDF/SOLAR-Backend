# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0003_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='recursal',
            field=models.BooleanField(default=False),
        ),
    ]
