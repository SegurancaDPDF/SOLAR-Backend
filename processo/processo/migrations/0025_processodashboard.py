# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0024_auto_20180626_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessoDashboard',
            fields=[
            ],
            options={
                'verbose_name': 'Processos - Dashboard',
                'proxy': True,
                'verbose_name_plural': 'Processos - Dashboard',
            },
            bases=('processo.processo',),
        ),
    ]
