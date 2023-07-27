# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0021_remove_servidor_profissao'),
        ('nadep', '0042_prisao_data_liquidacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='MotivoBaixaPrisao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='nadep_motivobaixaprisao_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='nadep_motivobaixaprisao_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='nadep_motivobaixaprisao_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Motivo para Baixa de Pris\xe3o',
                'verbose_name_plural': 'Motivos para Baixa de Pris\xe3o',
            },
        ),
        migrations.AddField(
            model_name='prisao',
            name='baixado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='prisao',
            name='data_baixa',
            field=models.DateField(null=True, verbose_name='Data da Baixa', blank=True),
        ),
        migrations.AlterField(
            model_name='historico',
            name='evento',
            field=models.SmallIntegerField(verbose_name='Evento', choices=[(1, 'Pris\xe3o'), (2, 'Soltura'), (3, 'Atendimento'), (4, 'Visita'), (5, 'Condena\xe7\xe3o'), (6, 'Falta'), (7, 'Regress\xe3o'), (8, 'Progress\xe3o'), (9, 'Mudan\xe7a de Regime'), (10, 'Transfer\xeancia'), (11, 'Conversao de Pena'), (12, 'Liquida\xe7\xe3o de Pena'), (13, 'Baixa de Pena')]),
        ),
        migrations.AddField(
            model_name='prisao',
            name='motivo_baixa',
            field=models.ForeignKey(verbose_name='Motivo da Baixa', blank=True, to='nadep.MotivoBaixaPrisao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
