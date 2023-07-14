# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0036_defensoria_tipo_painel_de_acompanhamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='pode_vincular_tarefa_de_cooperacao',
            field=models.BooleanField(default=False, help_text='Aten\xe7\xe3o! Setores que participam do atendimento v\xe3o aparecer mesmo se esta op\xe7\xe3o estiver desmarcada', verbose_name='Pode vincular tarefa de coopera\xe7\xe3o?'),
        ),
        migrations.AlterField(
            model_name='defensoria',
            name='pode_vincular_processo_judicial',
            field=models.BooleanField(default=True, verbose_name='Pode vincular processo judicial?'),
        ),
    ]
