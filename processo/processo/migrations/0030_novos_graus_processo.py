# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0029_partehistoricotransferencia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processo',
            name='grau',
            field=models.SmallIntegerField(default=None, null=True, blank=True, choices=[(1, '1\xba Grau'), (2, '2\xba Grau'), (3, 'STF/STJ')]),
        ),
    ]
