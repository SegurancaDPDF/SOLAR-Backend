# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

def migrate_data(apps, schema_editor):
    Tarefa = apps.get_model("atendimento", "Tarefa")

    # -1 (antigo) -> 4 (novo) código para prioridade alerta
    total = Tarefa.objects.filter(prioridade=-1, resposta_para__isnull=True).update(prioridade=4)
    print ('\nMigração de alertas finalizada: {} registros afetados!'.format(total))

    total = Tarefa.objects.filter(prioridade=-1, resposta_para__isnull=False).update(prioridade=5)
    print ('\nMigração de cooperações finalizada: {} registros afetados!'.format(total))

def reverse_migrate_data(apps, schema_editor):
    Tarefa = apps.get_model("atendimento", "Tarefa")

    # 4 (alerta) e 5 (cooperação) -> -1 (antigo) código para prioridade alerta
    total = Tarefa.objects.filter(prioridade__in=[4,5]).update(prioridade=-1)
    print ('\nMigração de alertas/cooperações finalizada: {} registros afetados!'.format(total))


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0028_add_area_acao'),
        ('atendimento', '0075_atendimento_exibir_no_painel_de_acompanhamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefa',
            name='processo',
            field=models.ForeignKey(default=None, blank=True, to='processo.Processo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='tarefa',
            name='prioridade',
            field=models.SmallIntegerField(default=None, null=True, blank=True, choices=[(0, 'Urgente'), (1, 'Alta'), (2, 'Normal'), (3, 'Baixa'), (4, 'Alerta'), (5, 'Coopera\xe7\xe3o')]),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
        migrations.AlterField(
            model_name='qualificacao',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=10, choices=[(10, 'Pedido'), (20, 'Atividade'), (30, 'Anota\xe7\xe3o'), (40, 'Tarefa')]),
        ),
    ]
