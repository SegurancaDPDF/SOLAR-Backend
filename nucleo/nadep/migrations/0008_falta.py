# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('assistido', '0002_auto_20150525_0835'),
        ('nadep', '0007_auto_20151026_1518'),
    ]

    operations = [
        migrations.CreateModel(
            name='Falta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_fato', models.DateTimeField(null=True, verbose_name='Data do Fato', blank=True)),
                ('numero_pad', models.CharField(max_length=255, verbose_name='N\xfamero PAD')),
                ('observacao', models.TextField(default=None, null=True, verbose_name='Observa\xe7\xe3o', blank=True)),
                ('resultado', models.SmallIntegerField(default=0, verbose_name='Tipo', choices=[(0, 'Aguardando Julgamento'), (1, 'Procedente'), (2, 'Improcedente')])),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('pessoa', models.ForeignKey(to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
    ]
