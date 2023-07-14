# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields

def carga_inicial(apps, schema_editor):
    default_data = (
        (10, 'Travesti'),
        (20, 'Mulher Transexual'),
        (30, 'Homem Transexual'),
        (40, 'Não se aplica'),
        (50, 'Ignorado'),
    )

    for pk, nome in default_data:
        IdentidadeGenero = apps.get_model('contrib', 'IdentidadeGenero')
        IdentidadeGenero(id=pk, nome=nome).save()


def reverse_carga_inicial(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0041_orientacaosexual'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdentidadeGenero',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=256)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='contrib_identidadegenero_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='contrib_identidadegenero_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='contrib_identidadegenero_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Identidade de G\xeanero',
                'verbose_name_plural': 'Identidades de G\xeanero',
            },
        ),
        migrations.RunPython(
            code=carga_inicial,
            reverse_code=reverse_carga_inicial,
        ),
        migrations.RunSQL(
            sql='ALTER SEQUENCE contrib_identidadegenero_id_seq RESTART WITH 101;',
            reverse_sql=''
        ),
    ]
