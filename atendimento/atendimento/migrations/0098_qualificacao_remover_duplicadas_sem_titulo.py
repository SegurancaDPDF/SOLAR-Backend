# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def migrate_data(apps, schema_editor):
    Atendimento = apps.get_model("atendimento", "Atendimento")
    Qualificacao = apps.get_model("atendimento", "Qualificacao")

    print('\nVerificando qualificações sem título e duplicadas')

    # Procura por todas qualificações sem título distinguidas por área, núcleo e especializado
    qualificacoes = Qualificacao.objects.filter(
        titulo_norm='',
        ativo=True
    ).order_by(
        'area_id',
        'nucleo_id',
        'especializado_id',
        'id'
    ).distinct(
        'area_id',
        'nucleo_id',
        'especializado_id'
    )

    # Passsa pelas qualificações distintas
    for qualificacao in qualificacoes:
        # Remaneja atendimentos de qualificações repetidas para qualificação principal
        atendimentos = Atendimento.objects.filter(
            qualificacao__titulo_norm='',
            qualificacao__area=qualificacao.area,
            qualificacao__nucleo=qualificacao.nucleo,
            qualificacao__especializado=qualificacao.especializado
        ).exclude(
            qualificacao=qualificacao
        ).update(
            qualificacao=qualificacao
        )
        # Desativa qualificações repetidas
        duplicadas = Qualificacao.objects.filter(
            titulo_norm='',
            area=qualificacao.area,
            nucleo=qualificacao.nucleo,
            especializado=qualificacao.especializado_id
        ).exclude(
            id=qualificacao.id
        ).update(
            ativo=False
        )

        print('{} atendimentos de {} qualificações duplicadas foram transferidos para qualificacao {} (área: {})'.format(
            atendimentos,
            duplicadas,
            qualificacao.id,
            qualificacao.area_id
        ))

    # Exclui qualificações inativas sem título e sem vínculo com atendimentos
    qualificacoes = Qualificacao.objects.filter(titulo_norm='', ativo=False, atendimento=None)
    print('{} qualificações duplicadas serão excluídas!'.format(qualificacoes.count()))
    qualificacoes.delete()


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0097_atendimento_tipo_coletividade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qualificacao',
            name='titulo_norm',
            field=models.CharField(default='', max_length=255, db_index=True),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
