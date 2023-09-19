# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0075_atendimento_exibir_no_painel_de_acompanhamento'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processo', '0028_add_area_acao'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParteHistoricoTransferencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('atendimento_antigo', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='atendimento.Defensor')),
                ('atendimento_novo', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='atendimento.Defensor')),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='processo_partehistoricotransferencia_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='processo_partehistoricotransferencia_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='processo_partehistoricotransferencia_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('parte', models.ForeignKey(related_name='historicos_transferencias', on_delete=django.db.models.deletion.PROTECT, to='processo.Parte')),
            ],
            options={
                'ordering': ['parte', 'cadastrado_em'],
                'verbose_name': 'Historico de Transferencia de Parte',
                'verbose_name_plural': 'Historico de Transferencias de Partes'
            },
        ),
    ]
