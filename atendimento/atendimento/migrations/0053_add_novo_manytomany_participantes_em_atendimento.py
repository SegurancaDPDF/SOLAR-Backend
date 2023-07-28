# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0019_cargo'),
        ('atendimento', '0052_add_model_atendimento_participante'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='participantes_novo',
            field=models.ManyToManyField(related_name='atendimentos_novo', through='atendimento.AtendimentoParticipante', to='contrib.Servidor', blank=True),
        ),
    ]
