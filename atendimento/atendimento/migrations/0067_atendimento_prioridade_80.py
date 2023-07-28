# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bulk_update.helper import bulk_update
from django.db import migrations, models


def reverse_migrate_data(apps, schema_editor):
    Atendimento = apps.get_model("atendimento", "Atendimento")

    total = 0

    while Atendimento.objects.filter(prioridade=False, prioridade2__gt=10).exists():

        atendimentos = Atendimento.objects.filter(
            prioridade=False,
            prioridade2__gt=10
        ).order_by()[:1000]

        for a in atendimentos:
            a.prioridade = True

        bulk_update(atendimentos, update_fields=['prioridade'], batch_size=1000)

        total += atendimentos.count()
        print("Em progresso: {}".format(total))

    print ('\nMigração reverse finalizada. {} registros afetados!'.format(total))


def migrate_data(apps, schema_editor):
    Atendimento = apps.get_model("atendimento", "Atendimento")

    total = 0

    while Atendimento.objects.filter(prioridade=True, prioridade2=0).exists():

        atendimentos = Atendimento.objects.filter(
            prioridade=True,
            prioridade2=0
        ).order_by()[:1000]

        for a in atendimentos:
            a.prioridade2 = 10

        bulk_update(atendimentos, update_fields=['prioridade2'], batch_size=1000)

        total += atendimentos.count()
        print("Em progresso: {}".format(total))

    print ('\nMigração finalizada. {} registros afetados!'.format(total))


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ('atendimento', '0066_qualificacao_conta_estatistica'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='prioridade2',
            field=models.PositiveSmallIntegerField(
                default=0,
                null=False,
                choices=[
                    (0, 'Sem prioridade'),
                    (10, 'Prioridade'),
                    (20, 'Prioridade +80')
                ]
            ),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        )
    ]
