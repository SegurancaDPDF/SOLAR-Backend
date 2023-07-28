# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0053_add_novo_manytomany_participantes_em_atendimento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='atendimento',
            name='participantes',
        ),
        migrations.RenameField(
            model_name='atendimento',
            old_name='participantes_novo',
            new_name='participantes',
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='participantes',
            field=models.ManyToManyField(related_name='atendimentos', through='atendimento.AtendimentoParticipante', to='contrib.Servidor', blank=True),
        ),
    ]
