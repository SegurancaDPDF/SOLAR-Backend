# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0040_manifestacao_tipo_evento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processo',
            name='valor_causa',
            field=models.FloatField(default=0, verbose_name='Valor da Causa'),
        ),
    ]
