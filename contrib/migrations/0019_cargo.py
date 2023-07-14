# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models, connection
import django.db.models.deletion
from django.conf import settings
import cuser.fields

from assistido.models import Profissao
from contrib.models import Cargo, Util


def populate_new_cargo_fields(apps, schema_editor):
    """
    Popula a tabela de Cargos com as profissões vinculadas aos servidores
    """

    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT profissao_id FROM contrib_servidor WHERE profissao_id IS NOT NULL;')
    rows = cursor.fetchall()

    profissoes_id = []

    for row in rows:
        profissoes_id.append(row[0])

    profissoes = Profissao.objects.filter(id__in=profissoes_id).exclude(nome='').values('nome')

    cargos = []
    for profissao in profissoes:
        cargos.append(
            Cargo(nome=profissao['nome'], nome_norm=Util.normalize(profissao['nome']))
        )
    Cargo.objects.bulk_create(cargos)


def populate_new_cargo_fields_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0018_auto_20180530_1010'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512, db_index=True)),
                ('nome_norm', models.CharField(max_length=512, db_index=True)),
                ('codigo', models.CharField(max_length=512, db_index=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='contrib_cargo_cadastrado_por',
                                                                 on_delete=django.db.models.deletion.SET_NULL,
                                                                 editable=False,
                                                                 to=settings.AUTH_USER_MODEL,
                                                                 null=True)),
                ('desativado_por', models.ForeignKey(related_name='contrib_cargo_desativado_por',
                                                     on_delete=django.db.models.deletion.SET_NULL,
                                                     blank=True,
                                                     to=settings.AUTH_USER_MODEL,
                                                     null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='contrib_cargo_modificado_por',
                                                                 on_delete=django.db.models.deletion.SET_NULL,
                                                                 editable=False,
                                                                 to=settings.AUTH_USER_MODEL,
                                                                 null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(populate_new_cargo_fields, populate_new_cargo_fields_reverse),
    ]
