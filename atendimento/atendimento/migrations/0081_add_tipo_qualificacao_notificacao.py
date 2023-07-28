# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0080_vincula_atendimento_recepcao_ao_agendamento_original'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='qualificacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='atendimento.Qualificacao', null=True, verbose_name='Qualifica\xe7\xe3o'),
        ),
        migrations.AlterField(
            model_name='qualificacao',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=10, choices=[(10, 'Pedido'), (20, 'Atividade'), (30, 'Anota\xe7\xe3o'), (31, 'Notifica\xe7\xe3o (chatbot)'), (40, 'Tarefa')]),
        ),
    ]
