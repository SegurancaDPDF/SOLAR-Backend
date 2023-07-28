# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0011_defensoria_grau'),
        ('atendimento', '0034_auto_20170531_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='TarefaVisualizacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visualizada_em', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('tarefa', models.ForeignKey(related_name='visualizacoes', to='atendimento.Tarefa', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('visualizada_por', models.ForeignKey(related_name='+', to='contrib.Servidor', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'db_table': 'atendimento_tarefa_visualizacao',
            },
        ),
    ]
