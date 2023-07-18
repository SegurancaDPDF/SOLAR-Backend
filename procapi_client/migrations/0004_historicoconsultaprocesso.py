# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields

# Classe de migração do Django, usado para criar uma nova tabela no banco de dados.
# As operações definidas na migração são responsáveis por criar o modelo "HistoricoConsultaProcesso" no banco de dados.

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('procapi_client', '0003_historicoconsultadocumento'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoConsultaProcesso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('processo', models.CharField(db_index=True, max_length=50, null=True, verbose_name='Processo', blank=True)),
                ('ip', models.CharField(db_index=True, max_length=15, null=True, verbose_name='Endere\xe7o IP', blank=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='procapi_client_historicoconsultaprocesso_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='procapi_client_historicoconsultaprocesso_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='procapi_client_historicoconsultaprocesso_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-cadastrado_em'],
                'verbose_name': 'Hist\xf3rico Consulta de Processo (log de acesso de usu\xe1rios)',
                'verbose_name_plural': 'Hist\xf3ricos Consulta de Processo (log de acesso de usu\xe1rios)',
            },
        ),
        migrations.AddField(
            model_name='historicoconsultadocumento',
            name='ip',
            field=models.CharField(db_index=True, max_length=15, null=True, verbose_name='Endere\xe7o IP', blank=True),
        ),
    ]
