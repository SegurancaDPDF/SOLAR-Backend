# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0005_area_penal'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servidor',
            options={'ordering': ['nome'], 'verbose_name': 'Servidor', 'verbose_name_plural': 'Servidores'},
        ),
    ]
