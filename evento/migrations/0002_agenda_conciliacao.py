# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evento', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agenda',
            name='conciliacao',
            field=models.TextField(default=None, null=True, blank=True),
        ),
    ]
