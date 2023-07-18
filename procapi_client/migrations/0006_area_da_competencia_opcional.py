# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

# Classe de migração que altera um campo em um modelo existente. 
class Migration(migrations.Migration):

    dependencies = [
        ('procapi_client', '0005_competencia_sistemawebservice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competencia',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, verbose_name='\xc1rea da Compet\xeancia', to='contrib.Area', null=True),
        ),
    ]
