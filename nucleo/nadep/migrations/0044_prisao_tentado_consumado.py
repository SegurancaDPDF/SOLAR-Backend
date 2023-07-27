# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0043_movito_baixa_de_prisao'),
    ]

    operations = [
        migrations.AddField(
            model_name='prisao',
            name='tentado_consumado',
            field=models.SmallIntegerField(default=None, null=True, verbose_name='Tentado/Consumado', blank=True, choices=[(10, 'Tentado'), (20, 'Consumado')]),
        ),
    ]
