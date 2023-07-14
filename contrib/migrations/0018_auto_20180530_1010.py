# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0017_auto_20180509_0844'),
    ]

    operations = [
        migrations.AddField(
            model_name='salario',
            name='indice_renda_familiar',
            field=models.DecimalField(default=0, max_digits=16, decimal_places=2),
        ),
        migrations.AddField(
            model_name='salario',
            name='indice_renda_individual',
            field=models.DecimalField(default=0, max_digits=16, decimal_places=2),
        ),
        migrations.AddField(
            model_name='salario',
            name='indice_renda_per_capita',
            field=models.DecimalField(default=0, max_digits=16, decimal_places=2),
        ),
        migrations.AddField(
            model_name='salario',
            name='indice_valor_bens',
            field=models.DecimalField(default=0, max_digits=16, decimal_places=2),
        ),
        migrations.AddField(
            model_name='salario',
            name='indice_valor_investimentos',
            field=models.DecimalField(default=0, max_digits=16, decimal_places=2),
        ),
    ]
