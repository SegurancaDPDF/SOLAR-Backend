# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0015_auto_20151124_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='prisao',
            name='fracao_lc',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Fra\xe7\xe3o LC', choices=[(13, '1/3 - Comum Prim\xe1rio'), (12, '1/2 - Comum Reicidente'), (23, '2/3 - Hediondo'), (11, '1/1 - Hediondo Reicidente')]),
        ),
        migrations.AddField(
            model_name='prisao',
            name='fracao_pr',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Fra\xe7\xe3o PR', choices=[(16, '1/6 - Comum'), (25, '2/5 - Hediondo Prim\xe1rio'), (35, '3/5 - Hediondo Reicidente')]),
        ),
    ]
