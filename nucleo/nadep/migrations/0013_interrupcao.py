# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('assistido', '0002_auto_20150525_0835'),
        ('nadep', '0012_auto_20151113_0948'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interrupcao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_inicial', models.DateField(verbose_name='Data Inicial')),
                ('data_final', models.DateField(verbose_name='Data Final')),
                ('observacao', models.TextField(default=None, null=True, verbose_name='Observa\xe7\xe3o', blank=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('pessoa', models.ForeignKey(to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
    ]
