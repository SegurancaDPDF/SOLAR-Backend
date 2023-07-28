# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Atendimento = apps.get_model("atendimento", "Atendimento")
    Qualificacao = apps.get_model("atendimento", "Qualificacao")

    atendimentos = Atendimento.objects.select_related('qualificacao').filter(qualificacao__titulo_norm='')

    for atendimento in atendimentos:

        nova = Qualificacao.objects.filter(
            area_id=atendimento.qualificacao.area_id,
            titulo_norm=atendimento.qualificacao.titulo_norm
        ).order_by('id').first()

        print(atendimento.numero, atendimento.qualificacao.id, nova.id)

        atendimento.qualificacao = nova
        atendimento.save()

    total = Qualificacao.objects.filter(
        titulo_norm='',
        atendimento=None
    ).delete()

    print('{} qualificações duplicadas excluídas!'.format(total))


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0076_tarefa_cooperacao'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
