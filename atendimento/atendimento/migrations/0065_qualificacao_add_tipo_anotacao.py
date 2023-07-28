# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Qualificacao = apps.get_model("atendimento", "Qualificacao")
    Qualificacao.objects.exclude(tipo__in=[10, 20]).update(ativo=False)


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0064_tarefa_preencher_setor_responsavel'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
        migrations.AlterField(
            model_name='qualificacao',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=10, choices=[(10, 'Pedido'), (20, 'Atividade'), (30, 'Anota\xe7\xe3o')]),
        ),
    ]
