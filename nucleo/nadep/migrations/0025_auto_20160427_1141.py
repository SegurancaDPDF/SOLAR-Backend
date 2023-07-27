# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('assistido', '0003_auto_20160406_1631'),
        ('nadep', '0024_auto_20160419_1049'),
    ]

    operations = [
        migrations.CreateModel(
            name='Historico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_registro', models.DateField(verbose_name='Data Registro')),
                ('evento', models.SmallIntegerField(verbose_name='Evento', choices=[(1, 'Pris\xe3o'), (2, 'Soltura'), (3, 'Atendimento'), (4, 'Visita'), (5, 'Condena\xe7\xe3o'), (6, 'Falta'), (7, 'Regress\xe3o'), (8, 'Progress\xe3o'), (9, 'Mudan\xe7a de Regime'), (10, 'Transfer\xeancia')])),
                ('historico', models.TextField(default=None, null=True, blank=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('pessoa', models.ForeignKey(to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['pessoa__nome', 'data_registro'],
                'verbose_name': 'Hist\xf3rico',
                'verbose_name_plural': 'Hist\xf3ricos',
            },
        ),
    ]
