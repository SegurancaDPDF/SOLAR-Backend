# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('data_inicial', models.DateField(verbose_name=b'Data In\xc3\xadcio')),
                ('data_final', models.DateField(verbose_name=b'Data T\xc3\xa9rmino')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name=b'Data de Cadastro', null=True)),
                ('data_autorizacao', models.DateTimeField(verbose_name=b'Data de Autoriza\xc3\xa7\xc3\xa3o', null=True, editable=False)),
                ('data_exclusao', models.DateTimeField(verbose_name=b'Data de Exclus\xc3\xa3o', null=True, editable=False)),
                ('ativo', models.BooleanField(default=True)),
                ('autorizado_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensoria', models.ForeignKey(to='contrib.Defensoria', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('municipio', models.ForeignKey(to='contrib.Municipio', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('participantes', models.ManyToManyField(to='contrib.Servidor')),
            ],
            options={
                'ordering': ['-ativo', 'data_inicial', 'defensoria__comarca'],
            },
        ),
    ]
