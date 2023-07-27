# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0044_prisao_tentado_consumado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prisao',
            name='resultado_sentenca',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Resultado da Senten\xe7a', choices=[(0, 'Absolvido'), (1, 'Condenado'), (2, 'Desclassificado'), (101, 'Absolvi\xe7\xe3o Impr\xf3pria - Interna\xe7\xe3o'), (102, 'Absolvi\xe7\xe3o Impr\xf3pria - Tratamento Ambulatorial')]),
        ),
    ]
