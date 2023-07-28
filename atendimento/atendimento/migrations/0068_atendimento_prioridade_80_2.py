# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ('atendimento', '0067_atendimento_prioridade_80'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='atendimento',
            name='prioridade'
        ),
        migrations.RenameField(
            model_name='atendimento',
            old_name='prioridade2',
            new_name='prioridade',
        ),
    ]
