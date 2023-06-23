# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bulk_update.helper import bulk_update
from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Atuacao = apps.get_model("defensor", "Atuacao")

    TIPO_SUBSTITUICAO = 0
    TIPO_ACUMULACAO = 1
    TIPO_TITULARIDADE = 2

    total = 0

    while Atuacao.objects.filter(
        pode_assinar_ged=False,
        tipo__in=[
            TIPO_TITULARIDADE,
            TIPO_ACUMULACAO,
            TIPO_SUBSTITUICAO
        ],
        ativo=True
    ).exists():

        atuacoes = Atuacao.objects.filter(
            pode_assinar_ged=False,
            tipo__in=[
                TIPO_TITULARIDADE,
                TIPO_ACUMULACAO,
                TIPO_SUBSTITUICAO
            ],
            ativo=True
        ).order_by()[:500]

        for a in atuacoes:
            a.pode_assinar_ged = True

        bulk_update(atuacoes, update_fields=['pode_assinar_ged'], batch_size=1000)

        total += atuacoes.count()
        print("Em progresso: {}".format(total))

    print ('\nMigração finalizada. {} registros afetados!'.format(total))


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0012_auto_20190411_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='atuacao',
            name='pode_assinar_ged',
            field=models.BooleanField(default=False, verbose_name='Pode assinar GED?'),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data
        )
    ]
