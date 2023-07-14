# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0027_auto_20180829_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salario',
            name='indice_renda_familiar',
            field=models.DecimalField(default=0, verbose_name='\xcdndice de renda familiar', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='salario',
            name='indice_renda_individual',
            field=models.DecimalField(default=0, verbose_name='\xcdndice de renda individual', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='salario',
            name='indice_renda_per_capita',
            field=models.DecimalField(default=0, verbose_name='\xcdndice de renda per capita', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='salario',
            name='indice_valor_bens',
            field=models.DecimalField(default=0, verbose_name='\xcdndice de valor em bens', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='salario',
            name='indice_valor_investimentos',
            field=models.DecimalField(default=0, verbose_name='\xcdndice de valor em investimentos', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='salario',
            name='indice_valor_salario_funcionario',
            field=models.DecimalField(default=0, verbose_name='\xcdndice de sal\xe1rio do funcion\xe1rio', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='salario',
            name='tipo_pessoa',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='Tipo de pessoa', choices=[(0, 'Pessoa F\xedsica'), (1, 'Pessoa Jur\xeddica')]),
        ),
    ]
