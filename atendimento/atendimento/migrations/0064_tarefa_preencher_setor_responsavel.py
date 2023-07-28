# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bulk_update.helper import bulk_update
from django.db import migrations, models


def migrate_data(apps, schema_editor):

    Tarefa = apps.get_model("atendimento", "Tarefa")

    tarefas = Tarefa.objects.select_related(
        'atendimento__defensor'
    ).filter(
        setor_responsavel=None
    ).exclude(
        atendimento__defensor=None
    ).only(
        'atendimento__defensor__defensoria_id'
    )

    total_registros = tarefas.count()

    if total_registros:

        print('\nPreenchendo campo "setor_responsavel" das tarefas...')

        for tarefa in tarefas:

            print(tarefa.id, tarefa.atendimento.numero)

            if tarefa.atendimento and hasattr(tarefa.atendimento, 'defensor'):
                tarefa.setor_responsavel_id = tarefa.atendimento.defensor.defensoria_id
            else:
                tarefa.setor_responsavel_id = None

        print('Registrando alteracao no banco de dados...')

        bulk_update(tarefas, update_fields=['setor_responsavel_id'], batch_size=1000)

        print('{} registros afetados!'.format(total_registros))


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0063_perm_requalificar_atendimento_retroativo'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
