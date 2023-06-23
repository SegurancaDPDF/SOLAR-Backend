# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0005_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefensorAssessor',
            fields=[
            ],
            options={
                'verbose_name': 'Defensor (Assessor)',
                'proxy': True,
                'verbose_name_plural': 'Defensores (Assessores)',
            },
            bases=('defensor.defensor',),
        ),
        migrations.CreateModel(
            name='DefensorSupervisor',
            fields=[
            ],
            options={
                'verbose_name': 'Defensor (Supervisor)',
                'proxy': True,
                'verbose_name_plural': 'Defensores (Supervisores)',
            },
            bases=('defensor.defensor',),
        ),
    ]
