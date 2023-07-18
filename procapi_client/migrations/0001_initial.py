# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import unicode_literals

from django.db import migrations, models


# Classe de migração
 # Criação do modelo HistoricoConsultaProcessos
class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoConsultaProcessos',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_inicial', models.DateTimeField(verbose_name='Data Inicial', editable=False)),
                ('data_final', models.DateTimeField(verbose_name='Data Final', editable=False, db_index=True)),
                ('paginas', models.IntegerField(null=True)),
                ('registros', models.IntegerField(null=True)),
                ('sucesso', models.BooleanField(default=False, db_index=True)),
            ],
            options={
                'ordering': ['-data_final'],
                'verbose_name': 'Hist\xf3rico Consulta de Processos',
                'verbose_name_plural': 'Hist\xf3ricos Consulta de Processos',
            },
        ),
    ]
