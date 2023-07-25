# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0037_manifestacaoaviso'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifestacaodocumento',
            name='posicao',
            field=models.IntegerField(default=0),
        ),
    ]
