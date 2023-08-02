# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

from assistido.models import Situacao

import cuser.fields


def carga_inicial(apps, schema_editor):
    default_data = (
        (Situacao.CODIGO_PNE, 'Portador de Necessidades Especiais (PNE)'),
        (Situacao.CODIGO_IDOSO, 'Idoso'),
        (Situacao.CODIGO_FALECIDO, 'Falecido'),
        (Situacao.CODIGO_PRESO, 'Preso')
    )

    for codigo, nome in default_data:
        s = Situacao(nome=nome, codigo=codigo)
        s.save()


def reverse_carga_inicial(apps, schema_editor):
    pass


def altera_perfil_campos_obrigatorios(apps, schema_editor):
    PerfilCamposObrigatorio = apps.get_model('assistido', 'PerfilCamposObrigatorios')

    perfis = PerfilCamposObrigatorio.objects.all()

    for perfil in perfis:
        perfil.configuracao = perfil.configuracao.replace('"pne"', '"situacoes"')
        perfil.save()


def reverse_altera_perfil_campos_obrigatorios(apps, schema_editor):
    PerfilCamposObrigatorio = apps.get_model('assistido', 'PerfilCamposObrigatorios')

    perfis = PerfilCamposObrigatorio.objects.all()

    for perfil in perfis:
        perfil.configuracao = perfil.configuracao.replace('"situacoes"', '"pne"')
        perfil.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistido', '0036_corrige_acentuacao_campos'),
        ('atendimento', '0080_vincula_atendimento_recepcao_ao_agendamento_original'),
    ]

    operations = [
        migrations.CreateModel(
            name='Situacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=256)),
                ('codigo', models.CharField(max_length=255, unique=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='assistido_situacao_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='assistido_situacao_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='assistido_situacao_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Situa\xe7\xe3o',
                'verbose_name_plural': 'Situa\xe7\xf5es',
            },
        ),
        migrations.RunPython(
            code=carga_inicial,
            reverse_code=reverse_carga_inicial,
        ),
        migrations.RunSQL(
            sql='ALTER SEQUENCE assistido_situacao_id_seq RESTART WITH 101;',
            reverse_sql=''
        ),
        migrations.RunPython(
            code=altera_perfil_campos_obrigatorios,
            reverse_code=reverse_altera_perfil_campos_obrigatorios,
        )
    ]
