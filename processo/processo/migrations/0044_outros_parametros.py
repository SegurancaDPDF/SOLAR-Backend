# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processo', '0043_fasetipo_codigo_cnj'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutroParametro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512)),
                ('tipo', models.SmallIntegerField(default=0, choices=[(0, 'Texto'), (1, 'N\xfamero'), (2, 'Data'), (3, 'Lista'), (4, 'Booleano')])),
                ('lista', models.CharField(max_length=255, null=True, blank=True)),
                ('codigo_mni', models.CharField(max_length=512)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='processo_outroparametro_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='processo_outroparametro_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='processo_outroparametro_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Outro Par\xe2metro',
                'verbose_name_plural': 'Outros Par\xe2metros',
            },
        ),
        migrations.CreateModel(
            name='ProcessoOutroParametro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor', models.CharField(max_length=255, null=True, blank=True)),
                ('outro_parametro', models.ForeignKey(to='processo.OutroParametro', on_delete=django.db.models.deletion.PROTECT)),
                ('processo', models.ForeignKey(to='processo.Processo', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['processo', 'outro_parametro'],
                'db_table': 'processo_processo_outros_parametros',
            },
        ),
        migrations.AddField(
            model_name='processo',
            name='outros_parametros',
            field=models.ManyToManyField(to='processo.OutroParametro', verbose_name='Outros Par\xe2metros', through='processo.ProcessoOutroParametro'),
        ),
        migrations.AlterUniqueTogether(
            name='processooutroparametro',
            unique_together=set([('processo', 'outro_parametro')]),
        ),
    ]
