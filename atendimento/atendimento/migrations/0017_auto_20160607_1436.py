# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0016_auto_20160509_1547'),
    ]

    operations = [
        migrations.CreateModel(
            name='Arvore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('conteudo', models.TextField(default=None, null=True, verbose_name='Conte\xfado', blank=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_modificacao', models.DateTimeField(verbose_name='Data de Modifica\xe7\xe3o', null=True, editable=False)),
            ],
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='numero',
            field=models.BigIntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='arvore',
            name='atendimento',
            field=models.OneToOneField(to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
