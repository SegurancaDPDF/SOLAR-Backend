# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itinerante', '0003_auto_20160223_1020'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evento',
            options={'ordering': ['-ativo', 'data_inicial', 'defensoria__comarca'], 'verbose_name': 'Itinerante', 'verbose_name_plural': 'Itinerantes', 'permissions': (('auth_evento', 'Can authorize evento'),)},
        ),
    ]
