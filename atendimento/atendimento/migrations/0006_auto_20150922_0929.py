# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('atendimento', '0005_auto_20150603_1048'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assunto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=256, verbose_name='T\xedtulo assunto')),
                ('codigo', models.CharField(max_length=256, null=True, verbose_name='C\xf3digo assunto', blank=True)),
                ('ordem', models.IntegerField()),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('data_exclusao', models.DateTimeField(null=True, verbose_name='Data de Exclusao', blank=True)),
                ('descricao', models.CharField(max_length=256, null=True, verbose_name='Desci\xe7\xe3o Completa do Assunto', blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('pai', models.ForeignKey(related_name='filhos', blank=True, to='atendimento.Assunto', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['pk', '-pai__pk', 'ativo', 'ordem'],
            },
        ),
        migrations.AddField(
            model_name='atendimento',
            name='assuntos',
            field=models.ForeignKey(related_name='assuntos', default=None, blank=True, to='atendimento.Assunto', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
