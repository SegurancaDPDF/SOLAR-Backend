# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0021_auto_20180124_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fase',
            name='usuario_eproc',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
    ]
