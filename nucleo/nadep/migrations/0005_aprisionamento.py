# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('nadep', '0004_auto_20150916_1445'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aprisionamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_inicial', models.DateTimeField(verbose_name='Data da In\xedcio')),
                ('data_final', models.DateTimeField(null=True, verbose_name='Data de T\xe9rmino', blank=True)),
                ('situacao', models.SmallIntegerField(default=0, verbose_name='Situa\xe7\xe3o', choices=[(0, 'Preso'), (1, 'Solto'), (2, 'Transferido')])),
                ('historico', models.TextField(default=None, null=True, blank=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('origem_cadastro', models.SmallIntegerField(default=0, verbose_name='Origem', choices=[(0, 'Registro'), (1, 'Pris\xe3o'), (2, 'Visita')])),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('estabelecimento_penal', models.ForeignKey(verbose_name='Estabelecimento Penal', to='nadep.EstabelecimentoPenal', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('prisao', models.ForeignKey(to='nadep.Prisao', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
    ]
