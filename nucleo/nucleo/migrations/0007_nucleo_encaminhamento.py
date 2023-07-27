# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0006_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='encaminhamento',
            field=models.BooleanField(default=True, help_text='Aceita receber atendimentos via encaminhamento?'),
        ),
    ]
