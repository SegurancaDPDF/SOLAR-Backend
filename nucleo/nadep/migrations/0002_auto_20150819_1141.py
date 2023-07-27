# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prisao',
            name='historico_pronuncia',
            field=models.TextField(default=None, null=True, verbose_name='Hist\xf3rico da Pron\xfancia', blank=True),
        ),
        migrations.AddField(
            model_name='prisao',
            name='resultado_pronuncia',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Resultado da Pron\xfancia', choices=[(0, 'Absolvido'), (1, 'Condenado')]),
        ),
        migrations.AlterField(
            model_name='prisao',
            name='data_transito_acusacao',
            field=models.DateField(null=True, verbose_name='Tr\xe2nsito em Julgado da Senten\xe7a para a Acusa\xe7\xe3o', blank=True),
        ),
        migrations.AlterField(
            model_name='prisao',
            name='data_transito_defensor',
            field=models.DateField(null=True, verbose_name='Tr\xe2nsito em Julgado da Senten\xe7a para o Defensor', blank=True),
        ),
        migrations.AlterField(
            model_name='prisao',
            name='tipo',
            field=models.SmallIntegerField(default=0, verbose_name='Tipo', choices=[(0, 'Provis\xf3rio'), (1, 'Condenado')]),
        ),
    ]
