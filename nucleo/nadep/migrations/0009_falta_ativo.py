# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0008_falta'),
    ]

    operations = [
        migrations.AddField(
            model_name='falta',
            name='ativo',
            field=models.BooleanField(default=True),
        ),
    ]
