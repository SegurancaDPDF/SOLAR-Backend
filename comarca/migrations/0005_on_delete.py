# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comarca', '0004_predio_telefone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guiche',
            name='comarca',
            field=models.ForeignKey(to='contrib.Comarca', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='guiche',
            name='predio',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to='comarca.Predio',
                null=True
            ),
        ),
    ]
