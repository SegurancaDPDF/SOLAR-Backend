# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0003_auto_20150612_1613'),
        ('atendimento', '0005_auto_20150603_1048'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acesso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_solicitacao', models.DateTimeField(default=None, null=True, blank=True)),
                ('data_concessao', models.DateTimeField(default=None, null=True, blank=True)),
                ('data_revogacao', models.DateTimeField(default=None, null=True, blank=True)),
                ('nivel', models.SmallIntegerField(default=0, choices=[(0, 'Consulta'), (1, 'Edi\xe7\xe3o'), (2, 'Administra\xe7\xe3o')])),
                ('ativo', models.BooleanField(default=True)),
                ('atendimento', models.ForeignKey(to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('concedido_por', models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensor', models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('revogado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('solicitado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
    ]
