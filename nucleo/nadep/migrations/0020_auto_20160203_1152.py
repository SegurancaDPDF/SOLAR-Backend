# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0019_prisao_data_base'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remissao',
            name='dias_remissao',
            field=models.DecimalField(verbose_name='Dias Remi\xe7\xe3o', max_digits=16, decimal_places=2),
        ),
    ]
