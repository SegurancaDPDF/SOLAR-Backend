# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propac', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipoanexodocumentopropac',
            name='ativo',
            field=models.BooleanField(default=True),
        ),
    ]
