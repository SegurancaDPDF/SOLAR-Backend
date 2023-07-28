# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0100_qualificacao_disponivel_para_agendamento_via_app'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tarefa',
            options={'ordering': ['-ativo', '-atendimento__numero', 'titulo'], 'permissions': (('view_all_tarefas', 'Pode ver todas tarefas do gabinete'),)},
        ),
    ]
