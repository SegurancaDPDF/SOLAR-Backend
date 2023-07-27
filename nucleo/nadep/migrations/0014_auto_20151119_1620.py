# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0013_interrupcao'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='estabelecimentopenal',
            options={'verbose_name': 'Estabelecimento Penal', 'verbose_name_plural': 'Estabelecimentos Penais'},
        ),
        migrations.AlterModelOptions(
            name='falta',
            options={'verbose_name': 'Falta', 'verbose_name_plural': 'Faltas'},
        ),
        migrations.AlterModelOptions(
            name='interrupcao',
            options={'verbose_name': 'Interrup\xe7\xe3o', 'verbose_name_plural': 'Interrup\xe7\xf5es'},
        ),
        migrations.AlterModelOptions(
            name='prisao',
            options={'verbose_name': 'Pris\xe3o', 'verbose_name_plural': 'Pris\xf5es'},
        ),
        migrations.AlterModelOptions(
            name='remissao',
            options={'verbose_name': 'Remi\xe7\xe3o', 'verbose_name_plural': 'Remi\xe7\xf5es'},
        ),
        migrations.AlterModelOptions(
            name='tipificacao',
            options={'verbose_name': 'Tipifica\xe7\xe3o', 'verbose_name_plural': 'Tipifica\xe7\xf5es'},
        ),
        migrations.AddField(
            model_name='prisao',
            name='reicidente',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tipificacao',
            name='tipo',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(0, 'Comum'), (1, 'Hediondo Prim\xe1rio')]),
        ),
    ]
