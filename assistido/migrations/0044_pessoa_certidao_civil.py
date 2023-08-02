# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import migrations, models

from assistido.models import PerfilCamposObrigatorios


def altera_perfil_campos_obrigatorios(apps, schema_editor):

    for perfil in PerfilCamposObrigatorios.objects.all():

        configuracao = perfil.configuracao_to_json()

        if 'CadastrarPessoa' in configuracao:
            configuracao['CadastrarPessoa']['certidao_numero'] = False
            configuracao['CadastrarPessoa']['certidao_tipo'] = False

        perfil.configuracao = json.dumps(configuracao)
        perfil.save()


def reverse_altera_perfil_campos_obrigatorios(apps, schema_editor):

    for perfil in PerfilCamposObrigatorios.objects.all():

        configuracao = perfil.configuracao_to_json()

        if 'CadastrarPessoa' in configuracao:
            configuracao['CadastrarPessoa'].pop('certidao_numero', None)
            configuracao['CadastrarPessoa'].pop('certidao_tipo', None)

        perfil.configuracao = json.dumps(configuracao)
        perfil.save()


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0043_add_documento_assinado'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='certidao_numero',
            field=models.CharField(default=None, max_length=32, blank=True, help_text='Novo modelo (32 d\xedgitos)', null=True, verbose_name='N\xba Certid\xe3o Civil'),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='certidao_tipo',
            field=models.CharField(default=None, choices=[('CN', 'Nascimento'), ('CC', 'Casamento')], max_length=2, blank=True, null=True, verbose_name='Tipo Certid\xe3o Civil'),
        ),
        migrations.RunPython(
            code=altera_perfil_campos_obrigatorios,
            reverse_code=reverse_altera_perfil_campos_obrigatorios,
        )
    ]
