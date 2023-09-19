# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0016_acao_inquerito'),
    ]

    operations = [
        migrations.AddField(
            model_name='acao',
            name='acao_penal',
            field=models.BooleanField(default=False, verbose_name='A\xe7\xe3o Penal'),
        ),
    ]
