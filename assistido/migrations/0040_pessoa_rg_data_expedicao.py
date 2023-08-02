# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import migrations, models

from assistido.models import PerfilCamposObrigatorios


def altera_perfil_campos_obrigatorios(apps, schema_editor):

    for perfil in PerfilCamposObrigatorios.objects.all():

        configuracao = perfil.configuracao_to_json()

        if 'CadastrarPessoa' in configuracao:
            configuracao['CadastrarPessoa']['rg_data_expedicao'] = False

        perfil.configuracao = json.dumps(configuracao)
        perfil.save()


def reverse_altera_perfil_campos_obrigatorios(apps, schema_editor):

    for perfil in PerfilCamposObrigatorios.objects.all():

        configuracao = perfil.configuracao_to_json()

        if 'CadastrarPessoa' in configuracao:
            configuracao['CadastrarPessoa'].pop('rg_data_expedicao')

        perfil.configuracao = json.dumps(configuracao)
        perfil.save()


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0039_patrimonial_assistido'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='rg_data_expedicao',
            field=models.DateField(default=None, null=True, verbose_name='Data expedi\xe7\xe3o RG', blank=True),
        ),
        migrations.RunPython(
            code=altera_perfil_campos_obrigatorios,
            reverse_code=reverse_altera_perfil_campos_obrigatorios,
        )
    ]
