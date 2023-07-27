# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0033_auto_20160725_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interrupcao',
            name='data_final',
            field=models.DateField(default=None, null=True, verbose_name='Data Final', blank=True),
        ),
    ]
