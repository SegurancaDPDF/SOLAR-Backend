# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0004_nucleo_recursal'),
    ]

    operations = [
        migrations.AddField(
            model_name='formulario',
            name='publico',
            field=models.BooleanField(default=False),
        ),
    ]
