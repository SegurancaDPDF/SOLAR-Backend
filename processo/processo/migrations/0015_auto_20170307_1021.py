# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0014_auto_20160921_0842'),
    ]

    operations = [
        migrations.AddField(
            model_name='acao',
            name='penal',
            field=models.BooleanField(default=False, verbose_name='Penal'),
        ),
        migrations.AlterField(
            model_name='acao',
            name='execucao_penal',
            field=models.BooleanField(default=False, verbose_name='Execu\xe7\xe3o Penal'),
        ),
    ]
