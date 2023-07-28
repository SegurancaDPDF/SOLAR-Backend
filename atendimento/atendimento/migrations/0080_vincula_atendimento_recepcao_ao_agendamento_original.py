# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Atendimento = apps.get_model("atendimento", "Atendimento")

    # Procura todos agendamentos liberados pela recepção antes do seu cadastro e que foram remarcados
    atendimentos = Atendimento.objects.prefetch_related(
        'atendimento_remarcado',
        models.Prefetch(
            'filhos',
            queryset=Atendimento.objects.filter(
                tipo=3,
                ativo=True
            )
        )
    ).filter(
        data_atendimento__isnull=True,
        atendimento_remarcado__isnull=False,
        filhos__tipo=3,  # Atendimento.TIPO_RECEPCAO (3)
        filhos__data_cadastro__lt=models.F('data_cadastro'),
        filhos__ativo=True
    ).order_by('id')

    print('{} registros serão afetados!'.format(atendimentos.count()))

    for atendimento in atendimentos:

        atendimento_recepcao = atendimento.filhos.all().first()
        atendimento_remarcado = atendimento.atendimento_remarcado.all().first()

        if atendimento_recepcao.tipo == 3 and atendimento_remarcado.remarcado_id == atendimento.id:

            atendimento_recepcao.origem = atendimento_remarcado
            atendimento_recepcao.save()

            print(atendimento_recepcao.numero, atendimento.numero, atendimento_remarcado.numero)

        else:

            print('Atenção! Informações inconsistentes para o atendimento {}'.format(atendimento_recepcao.numero))

    print('Concluído!')


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0079_arvore_data_exclusao'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
