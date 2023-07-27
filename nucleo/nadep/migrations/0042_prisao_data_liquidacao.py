# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0041_auto_20170203_0917'),
    ]

    operations = [
        migrations.AddField(
            model_name='prisao',
            name='data_liquidacao',
            field=models.DateField(null=True, verbose_name='Data da Liquida\xe7\xe3o da Pena', blank=True),
        ),
    ]
