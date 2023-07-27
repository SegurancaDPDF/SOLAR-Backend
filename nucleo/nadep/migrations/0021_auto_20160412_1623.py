# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('nadep', '0020_auto_20160203_1152'),
    ]

    operations = [
        migrations.CreateModel(
            name='PenaRestritiva',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('restricao', models.SmallIntegerField(verbose_name='Tipo', choices=[(1, 'Presta\xe7\xe3o Pecuni\xe1ria (CP Art. 43, I)'), (2, 'Perda de Bens e Valores (CP Art. 43, II)'), (4, 'Presta\xe7\xe3o de Servi\xe7o (CP Art. 43, IV)'), (5, 'Interdi\xe7\xe3o Tempor\xe1ria de Direitos (CP Art. 43, V)'), (6, 'Limita\xe7\xe3o de Fim de Semana (CP Art. 43, VI)')])),
                ('ativo', models.BooleanField(default=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'Pena Restritiva',
                'verbose_name_plural': 'Penas Restritivas',
            },
        ),
        migrations.CreateModel(
            name='RestricaoPrestacaoServico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_referencia', models.DateField(verbose_name='Data de Refer\xeancia')),
                ('horas_trabalhadas', models.DurationField(help_text='Formato DD HH:mm:ss ou HHH:mm:ss', verbose_name='Horas Trabalhadas')),
                ('ativo', models.BooleanField(default=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'Restri\xe7\xe3o - Presta\xe7\xe3o de Servi\xe7o',
                'verbose_name_plural': 'Restri\xe7\xe3o - Presta\xe7\xe3o de Servi\xe7o',
            },
        ),
        migrations.AddField(
            model_name='prisao',
            name='duracao_pena_horas',
            field=models.DurationField(help_text='Formato DD HH:mm:ss ou HHH:mm:ss', null=True, verbose_name='Dura\xe7\xe3o da Pena (Horas)', blank=True),
        ),
        migrations.AddField(
            model_name='prisao',
            name='pena',
            field=models.SmallIntegerField(default=0, verbose_name='Pena', choices=[(0, 'Privativa'), (1, 'Restritiva')]),
        ),
        migrations.AddField(
            model_name='restricaoprestacaoservico',
            name='prisao',
            field=models.ForeignKey(to='nadep.Prisao', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='penarestritiva',
            name='prisao',
            field=models.ForeignKey(to='nadep.Prisao', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterUniqueTogether(
            name='penarestritiva',
            unique_together=set([('prisao', 'restricao')]),
        ),
    ]
