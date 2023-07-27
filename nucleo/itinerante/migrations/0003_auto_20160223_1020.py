# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('itinerante', '0002_evento_atuacoes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evento',
            options={'ordering': ['-ativo', 'data_inicial', 'defensoria__comarca'], 'verbose_name': 'Itinerante', 'verbose_name_plural': 'Itinerantes'},
        ),
    ]
