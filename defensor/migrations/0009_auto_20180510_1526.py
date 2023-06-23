# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0008_auto_20170714_1233'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='defensor',
            options={'ordering': ['-ativo', '-eh_defensor', 'servidor__nome'], 'verbose_name': 'Defensor/Assessor', 'verbose_name_plural': 'Defensores/Assessores'},
        ),
    ]
