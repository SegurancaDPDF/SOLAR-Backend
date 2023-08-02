# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0021_perfilcamposobrigatorios_tipo_pessoa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patrimonio',
            name='tem_investimentos',
            field=models.BooleanField(default=False, verbose_name='Possui Aplica\xe7\xf5es ou Investimentos'),
        ),
        migrations.AlterField(
            model_name='patrimonio',
            name='valor_investimentos',
            field=models.DecimalField(default=0, help_text='Valor total, em R$, de aplica\xe7\xf5es ou investimentos financeiros', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='renda',
            name='salario_funcionario',
            field=models.DecimalField(default=0, help_text='Preencha com a maior remunera\xe7\xe3o paga mensalmente', verbose_name='Maior Remunera\xe7\xe3o', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='renda',
            name='tem_fins_lucrativos',
            field=models.BooleanField(default=False, help_text='Selecione caso seja Pessoa J\xfaridica e tenha fins lucrativos', verbose_name='Tem Fins Lucrativos'),
        ),
    ]
