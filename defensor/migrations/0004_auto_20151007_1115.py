# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0003_auto_20150612_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atuacao',
            name='defensoria',
            field=models.ForeignKey(related_name='all_atuacoes', to='contrib.Defensoria', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
