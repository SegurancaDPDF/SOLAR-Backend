# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0020_auto_20171129_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processo',
            name='numero_puro',
            field=models.CharField(unique=True, max_length=50, verbose_name='N\xfamero puro'),
        ),
    ]
