# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import F
import django.db.models.deletion

LISTA_ORIENTACAO_SEXUAL = (
    (10, 'Heterossexual'),
    (20, 'Homossexual'),
    (30, 'Bissexual')
)

def carregar_dados(apps, schema_editor):
    Pessoa = apps.get_model('assistido', 'Pessoa')

    Pessoa.objects.filter(
        tipo_orientacao_sexual__in=[10,20,30]
    ).update(
        orientacao_sexual=F('tipo_orientacao_sexual')
    )

def reverse_carregar_dados(apps, schema_editor):
    Pessoa = apps.get_model('assistido', 'Pessoa')
    Pessoa.objects.filter(
        orientacao_sexual__in=[10,20,30]
    ).update(
        tipo_orientacao_sexual=F('orientacao_sexual')
    )

def altera_perfil_campos_obrigatorios(apps, schema_editor):
    PerfilCamposObrigatorio = apps.get_model('assistido', 'PerfilCamposObrigatorios')

    perfis = PerfilCamposObrigatorio.objects.all()

    for perfil in perfis:
        perfil.configuracao = perfil.configuracao.replace('"tipo_orientacao_sexual"', '"orientacao_sexual"')
        perfil.save()

def reverse_altera_perfil_campos_obrigatorios(apps, schema_editor):
    PerfilCamposObrigatorio = apps.get_model('assistido', 'PerfilCamposObrigatorios')

    perfis = PerfilCamposObrigatorio.objects.all()

    for perfil in perfis:
        perfil.configuracao = perfil.configuracao.replace('"orientacao_sexual"', '"tipo_orientacao_sexual"')
        perfil.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0041_orientacaosexual'),
        ('assistido', '0031_pessoa_aderiu_luna_chatbot'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='orientacao_sexual',
            field=models.ForeignKey(blank=True, to='contrib.OrientacaoSexual', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.RunPython(
            code=carregar_dados,
            reverse_code=reverse_carregar_dados,
        ),
        migrations.RunPython(
            code=altera_perfil_campos_obrigatorios,
            reverse_code=reverse_altera_perfil_campos_obrigatorios,
        )
    ]
