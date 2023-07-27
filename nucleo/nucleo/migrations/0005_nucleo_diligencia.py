# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0004_nucleo_recursal'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='diligencia',
            field=models.BooleanField(default=False),
        ),
    ]
