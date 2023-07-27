# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0002_auto_20150819_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='prisao',
            name='resultado_sentenca',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Resultado da Senten\xe7a', choices=[(0, 'Absolvido'), (1, 'Condenado'), (2, 'Desclassificado')]),
        ),
        migrations.AlterField(
            model_name='prisao',
            name='resultado_pronuncia',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Resultado da Pron\xfancia', choices=[(0, 'Absolvido'), (1, 'Pronunciado'), (2, 'Desclassificado')]),
        ),
    ]
