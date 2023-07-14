# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0038_menuextra'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuextra',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]
