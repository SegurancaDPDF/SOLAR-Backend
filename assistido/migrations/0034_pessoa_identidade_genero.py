# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import F
import django.db.models.deletion

LISTA_IDENTIDADE_GENERO = (
    (10, 'Travesti'),
    (20, 'Mulher Transexual'),
    (30, 'Homem Transexual'),
    (40, 'Não se aplica'),
    (50, 'Ignorado'),
)

def carregar_dados(apps, schema_editor):
    Pessoa = apps.get_model('assistido', 'Pessoa')

    Pessoa.objects.filter(
        tipo_identidade_genero__in=[10,20,30,40,50]
    ).update(
        identidade_genero=F('tipo_identidade_genero')
    )

def reverse_carregar_dados(apps, schema_editor):
    Pessoa = apps.get_model('assistido', 'Pessoa')
    Pessoa.objects.filter(
        identidade_genero__in=[10,20,30,40,50]
    ).update(
        tipo_identidade_genero=F('identidade_genero')
    )

def altera_perfil_campos_obrigatorios(apps, schema_editor):
    PerfilCamposObrigatorio = apps.get_model('assistido', 'PerfilCamposObrigatorios')

    perfis = PerfilCamposObrigatorio.objects.all()

    for perfil in perfis:
        perfil.configuracao = perfil.configuracao.replace('"tipo_identidade_genero"', '"identidade_genero"')
        perfil.save()

def reverse_altera_perfil_campos_obrigatorios(apps, schema_editor):
    PerfilCamposObrigatorio = apps.get_model('assistido', 'PerfilCamposObrigatorios')

    perfis = PerfilCamposObrigatorio.objects.all()

    for perfil in perfis:
        perfil.configuracao = perfil.configuracao.replace('"identidade_genero"', '"tipo_identidade_genero"')
        perfil.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0042_identidadegenero'),
        ('assistido', '0033_remove_pessoa_tipo_orientacao_sexual'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='identidade_genero',
            field=models.ForeignKey(blank=True, to='contrib.IdentidadeGenero', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
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
