# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0014_add_campos_auditoria_pessoa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moradia',
            name='num_comodos',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='N\xba c\xf4modos', blank=True),
        ),
        migrations.AlterField(
            model_name='moradia',
            name='tipo',
            field=models.SmallIntegerField(default=5, verbose_name='Im\xf3vel', choices=[(5, 'N\xe3o Informado'), (0, 'Pr\xf3prio'), (1, 'Programa Habitacional (Doa\xe7\xe3o do Gov: Federal, Estadual ou Municipal)'), (2, 'Alugado'), (3, 'Cedido'), (4, 'Financiado')]),
        ),
    ]
