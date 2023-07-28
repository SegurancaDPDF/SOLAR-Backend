# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields

def migrate_data(apps, schema_editor):
    TipoColetividade = apps.get_model("atendimento", "TipoColetividade")

    TipoColetividade.objects.create(
        nome=u"Não - Individual",
        data_inicial=datetime.now(),
        conta_estatistica=True,
        individual=True
    )

    TipoColetividade.objects.create(
        nome=u"Sim - Coletivo Determinado",
        data_inicial=datetime.now(),
        conta_estatistica=True,
        coletivo=True
    )

    TipoColetividade.objects.create(
        nome=u"Sim - Coletivo Difuso",
        data_inicial=datetime.now(),
        conta_estatistica=True,
        difuso=True
    )


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atendimento', '0096_add_perm_change_all_agendamentos'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoColetividade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512, db_index=True)),
                ('data_inicial', models.DateTimeField(verbose_name='Data inicial')),
                ('data_final', models.DateTimeField(default=None, null=True, verbose_name='Data final', blank=True)),
                ('conta_estatistica', models.BooleanField(default=True, help_text='Conta Estat\xedstica?', verbose_name='Conta estat\xedsticas')),
                ('individual', models.BooleanField(default=False, help_text='O atendimento \xe9 para caso individual?', verbose_name='Atendimento individual?')),
                ('coletivo', models.BooleanField(default=False, help_text='O atendimento \xe9 para caso coletivo?', verbose_name='Atendimento coletivo?')),
                ('difuso', models.BooleanField(default=False, help_text='O atendimento \xe9 para caso de coletividade difusa?', verbose_name='Atendimento coletivo difuso?')),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='atendimento_tipocoletividade_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='atendimento_tipocoletividade_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='atendimento_tipocoletividade_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Tipo de Coletividade',
                'verbose_name_plural': 'Tipos de Coletividade',
            },
        ),
        migrations.AddField(
            model_name='atendimento',
            name='tipo_coletividade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='atendimento.TipoColetividade', null=True, verbose_name='Atendimento Coletivo'),
        ),
        migrations.AlterUniqueTogether(
            name='tipocoletividade',
            unique_together=set([('nome', 'data_inicial', 'data_final')]),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
