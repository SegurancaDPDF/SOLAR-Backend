# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0008_auto_20180118_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='diretoria',
            field=models.BooleanField(default=False, help_text='Tem acesso ao m\xf3dulo da Diretoria Regional?'),
        ),
        migrations.AddField(
            model_name='nucleo',
            name='dpg',
            field=models.BooleanField(default=False, help_text='Tem acesso ao m\xf3dulo do DPG?', verbose_name='DPG'),
        ),
    ]
