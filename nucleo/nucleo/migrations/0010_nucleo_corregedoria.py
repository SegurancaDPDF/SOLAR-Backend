# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0009_auto_20180209_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='corregedoria',
            field=models.BooleanField(default=False, help_text='Tem acesso ao m\xf3dulo da Corregedoria?'),
        ),
    ]
