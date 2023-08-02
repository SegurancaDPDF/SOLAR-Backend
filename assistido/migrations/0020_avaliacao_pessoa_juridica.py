# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0019_auto_20180827_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='renda',
            name='salario_funcionario',
            field=models.DecimalField(default=0, help_text='Preencha com o maior sal\xe1rio que \xe9 pago mensalmente', verbose_name='Maior sal\xe1rio de funcion\xe1rio', max_digits=16, decimal_places=2),
        ),
        migrations.AddField(
            model_name='renda',
            name='tem_fins_lucrativos',
            field=models.BooleanField(default=False, help_text='Selecione caso seja Pessoa J\xfaridica e tenha fins lucrativos', verbose_name='Tem fins lucrativos'),
        ),
    ]
