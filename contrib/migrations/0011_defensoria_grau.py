# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0010_auto_20170419_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='grau',
            field=models.SmallIntegerField(default=1, null=True, blank=True, choices=[(1, '1\xba Grau'), (2, '2\xba Grau')]),
        ),
    ]
