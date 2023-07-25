# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0022_auto_20180220_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processo',
            name='tipo',
            field=models.SmallIntegerField(default=2, choices=[(0, 'Extrajudicial'), (1, 'F\xedsico'), (2, 'Eletr\xf4nico'), (3, 'Processo Administrativo Disciplinar (PAD)')]),
        ),
    ]
