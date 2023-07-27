# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0038_calculoexecucaopenal'),
    ]

    operations = [
        migrations.AddField(
            model_name='prisao',
            name='prestacao_pecuniaria',
            field=models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
    ]
