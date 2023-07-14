# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0034_endereco_principal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='defensoria',
            old_name='encaminhamento_extra',
            new_name='aceita_encaminhamento_extra',
        ),
        migrations.RenameField(
            model_name='defensoria',
            old_name='encaminhamento_pauta',
            new_name='aceita_encaminhamento_pauta',
        ),
        migrations.AddField(
            model_name='defensoria',
            name='aceita_agendamento_extra',
            field=models.BooleanField(default=True, verbose_name='Aceita agendamento na extra-pauta?'),
        ),
        migrations.AddField(
            model_name='defensoria',
            name='aceita_agendamento_pauta',
            field=models.BooleanField(default=False, verbose_name='Aceita agendamento na pauta?'),
        ),
    ]
