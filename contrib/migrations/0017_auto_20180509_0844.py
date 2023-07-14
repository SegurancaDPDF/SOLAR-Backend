# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0016_remove_defensoria_endereco'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='encaminhamento_extra',
            field=models.BooleanField(default=True, verbose_name='Aceita encaminhamento na extra-pauta?'),
        ),
        migrations.AddField(
            model_name='defensoria',
            name='encaminhamento_pauta',
            field=models.BooleanField(default=True, verbose_name='Aceita encaminhamento na pauta?'),
        ),
    ]
