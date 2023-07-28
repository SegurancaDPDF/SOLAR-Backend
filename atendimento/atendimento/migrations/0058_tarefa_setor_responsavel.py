# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bulk_update.helper import bulk_update
from django.db import migrations, models
import django.db.models.deletion


def migrate_data(apps, schema_editor):

    Tarefa = apps.get_model("atendimento", "Tarefa")

    tarefas = Tarefa.objects.select_related(
        'atendimento__defensor'
    ).exclude(
        atendimento__defensor=None
    ).only(
        'atendimento__defensor__defensoria_id'
    )

    print('\nPreenchendo campo "setor_responsavel" das tarefas...')

    for tarefa in tarefas:
        if tarefa.atendimento and hasattr(tarefa.atendimento, 'defensor'):
            tarefa.setor_responsavel_id = tarefa.atendimento.defensor.defensoria_id
        else:
            tarefa.setor_responsavel_id = None

    print('Registrando alteracao no banco de dados...')
    if len(tarefas):
        bulk_update(tarefas, update_fields=['setor_responsavel_id'], batch_size=1000)

    print('Concluido!')


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0024_add_uso_interno_em_servidor'),
        ('atendimento', '0057_remove_prazo_resposta_documentos_enviados_pedido_de_apoio'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefa',
            name='setor_responsavel',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
