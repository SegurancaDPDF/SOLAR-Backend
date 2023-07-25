# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0008_auto_20151215_1153'),
        ('contrib', '0004_auto_20150611_0956'),
        ('honorarios', '0003_auto_20150831_0936'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analise',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('motivo', models.CharField(default=None, max_length=255, null=True, verbose_name='Motivo pend\xeancia')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='analise_cadastro', default=None, to='contrib.Servidor', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('fase', models.OneToOneField(related_name='analises', to='processo.Fase', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'An\xe1lise de Honor\xe1rio',
                'verbose_name_plural': 'An\xe1lise de Honor\xe1rios',
            },
        ),
    ]
