# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import unicode_literals

from django.db import migrations, models

# Classe de migração
# Adição de campos ao modelo HistoricoConsultaProcessos

class Migration(migrations.Migration):

    dependencies = [
        ('procapi_client', '0001_initial'), # Dependência da migração anterior
    ]

    operations = [
        migrations.AddField(
            model_name='historicoconsultaprocessos',
            name='inicio_consulta',
            field=models.DateTimeField(verbose_name='Data In\xedcio da Consulta', null=True, editable=False),
        ),
        migrations.AddField(
            model_name='historicoconsultaprocessos',
            name='termino_consulta',
            field=models.DateTimeField(verbose_name='Data T\xe9rmino da Consulta', null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='historicoconsultaprocessos',
            name='registros',
            field=models.IntegerField(null=True, db_index=True),
        ),
    ]
