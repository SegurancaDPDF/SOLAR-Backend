# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0018_auto_20151126_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='prisao',
            name='data_base',
            field=models.DateField(null=True, verbose_name='Data-Base', blank=True),
        ),
    ]
