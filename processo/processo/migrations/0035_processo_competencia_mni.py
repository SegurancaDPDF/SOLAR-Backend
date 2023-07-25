# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0034_manifestacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='competencia_mni',
            field=models.CharField(max_length=50, null=True, verbose_name='Compet\xeancia Judicial', blank=True),
        ),
    ]
