# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0004_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='pre_cadastro',
            field=models.BooleanField(default=False),
        ),
    ]
