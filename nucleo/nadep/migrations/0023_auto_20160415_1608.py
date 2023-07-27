# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('nadep', '0022_auto_20160413_1650'),
    ]

    operations = [
        migrations.CreateModel(
            name='MudancaRegime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.SmallIntegerField(verbose_name='Tipo', choices=[(0, 'Progress\xe3o'), (1, 'Regress\xe3o')])),
                ('regime', models.SmallIntegerField(verbose_name='Regime', choices=[(0, 'Fechado'), (1, 'Semiaberto'), (2, 'Aberto'), (3, 'Livramento'), (4, 'Medida de Seguran\xe7a')])),
                ('data_registro', models.DateTimeField(verbose_name='Data Registro')),
                ('data_base', models.DateTimeField(verbose_name='Data Base')),
                ('historico', models.TextField(default=None, null=True, blank=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('estabelecimento_penal', models.ForeignKey(verbose_name='Estabelecimento Penal', blank=True, to='nadep.EstabelecimentoPenal', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('prisao', models.ForeignKey(to='nadep.Prisao', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
        migrations.AlterModelOptions(
            name='restricaoprestacaoservico',
            options={'ordering': ('-ativo', 'prisao__pessoa__nome', 'data_referencia'), 'verbose_name': 'Restri\xe7\xe3o - Presta\xe7\xe3o de Servi\xe7o', 'verbose_name_plural': 'Restri\xe7\xe3o - Presta\xe7\xe3o de Servi\xe7o'},
        ),
        migrations.AlterField(
            model_name='aprisionamento',
            name='origem_cadastro',
            field=models.SmallIntegerField(default=0, verbose_name='Origem', choices=[(0, 'Registro'), (1, 'Pris\xe3o'), (2, 'Visita'), (3, 'Mudan\xe7a de Regime')]),
        ),
    ]
