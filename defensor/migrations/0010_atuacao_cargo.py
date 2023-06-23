# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models, connection
from django.db.models import Q
import django.db.models.deletion
from django.shortcuts import get_object_or_404

from contrib.models import Cargo
from defensor.models import Atuacao, Defensor


def populate_new_cargo_fields(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute('''SELECT DISTINCT defensor_defensor.id, assistido_profissao.nome
                      FROM defensor_defensor 
                      INNER JOIN contrib_servidor ON contrib_servidor.id = defensor_defensor.servidor_id
                      INNER JOIN assistido_profissao ON assistido_profissao.id = contrib_servidor.profissao_id
                      WHERE contrib_servidor.profissao_id IS NOT NULL
                      AND assistido_profissao.nome <> '';
                  ''')
    rows = cursor.fetchall()

    for defensor in rows:
        cargo = get_object_or_404(Cargo, nome=defensor[1])

        atuacoes = Atuacao.objects.filter(defensor_id=defensor[0], ativo=True, cargo=None)

        for atuacao in atuacoes:
            atuacao.cargo = cargo
            atuacao.save()


def populate_new_cargo_fields_reverse(apps, schema_editor):
    atuacoes = Atuacao.objects.filter(~Q(cargo=None))

    for atuacao in atuacoes:
        atuacao.cargo = None
        atuacao.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0019_cargo'),
        ('defensor', '0009_auto_20180510_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='atuacao',
            name='cargo',
            field=models.ForeignKey(related_name='all_atuacoes', default=None, blank=True, to='contrib.Cargo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.RunPython(populate_new_cargo_fields, populate_new_cargo_fields_reverse),
    ]
