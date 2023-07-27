# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='propac',
            field=models.BooleanField(default=False, help_text='Tem acesso ao m\xf3dulo de propacs?'),
        ),
    ]
