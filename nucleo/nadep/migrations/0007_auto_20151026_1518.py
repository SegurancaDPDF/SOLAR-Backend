# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0006_atendimento_estabelecimento_penal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prisao',
            name='resultado_pronuncia',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Resultado da Pron\xfancia', choices=[(0, 'Impronunciado'), (1, 'Pronunciado'), (2, 'Desclassificado')]),
        ),
    ]
