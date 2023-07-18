# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import unicode_literals

from django.db import migrations, models

# Classe de migração responsável por definir as alterações no esquema do banco de dados.
class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_atividades_extraordinarias'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtividadeExtraordinaria',
            fields=[
            ],
            options={
                'verbose_name': 'Atividade Extraordin\xe1ria',
                'proxy': True,
                'verbose_name_plural': 'Atividades Extraordin\xe1rias',
            },
            bases=('core.evento',),
        ),
        migrations.CreateModel(
            name='AtividadeExtraordinariaTipo',
            fields=[
            ],
            options={
                'verbose_name': 'Atividade Extraordin\xe1ria Tipo',
                'proxy': True,
                'verbose_name_plural': 'Atividades Extraordin\xe1rias Tipos',
            },
            bases=('core.tipoevento',),
        ),
    ]
