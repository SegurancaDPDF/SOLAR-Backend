# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0026_remove_bairros_duplicados'),
    ]

    operations = [
        migrations.AddField(
            model_name='salario',
            name='indice_valor_salario_funcionario',
            field=models.DecimalField(default=0, max_digits=16, decimal_places=2),
        ),
        migrations.AddField(
            model_name='salario',
            name='tipo_pessoa',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='Tipo', choices=[(0, 'Pessoa F\xedsica'), (1, 'Pessoa Jur\xeddica')]),
        ),
    ]
