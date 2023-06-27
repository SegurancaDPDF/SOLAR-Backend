# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indeferimento', '0002_indeferimento_defensoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indeferimento',
            name='resultado',
            field=models.SmallIntegerField(default=0, null=True, blank=True, choices=[(0, 'N\xe3o Avaliado'), (10, 'Deferimento'), (20, 'Indeferimento'), (30, 'Recebimento')]),
        ),
    ]
